from langchain.retrievers import EnsembleRetriever
from langsmith.run_helpers import traceable
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel
from operator import itemgetter
from src.utils.type_utils import TDTDoc
from typing import List
from src.rag.types import RAGResponse, RAGConfig
from src.service.provider import ProviderService
from src.custom.es_bm25_retriever import MyElasticSearchBM25Retriever
from src.service.applog import AppLogService

TEMPLATE = """You are a helpful admission assistant for Ton Duc Thang university who gives helpful and accurate information.
Answer the question mainly using the following context. Output "None" if you cannot answer:
```
{context}
```
Question: {question}
"""

TEMPLATE = """Bạn là một người tư vấn viên thân thiện và đầy hiểu biết. Nhiệm vụ của bạn là hỗ trợ người dùng hiểu biết hơn về trường đại học Tôn Đức Thắng.

Đây là thông tin mà bạn biết:
```
{context}
```
Hãy hỗ trợ thật tốt với yêu cầu sau đến từ người dùng.
Yêu cầu (Question): {question}
Hãy trả lời một cách thật ngắn gọn, xúc tích, cấu trúc câu đầy đủ. Output "None" if you cannot answer
"""


class HybridRFFGeminiRAG:
    """
        This is a RAG designed to search docs in vector store and provide answers to user.
        It uses:
        - Gemini as chat model
        - Gemini + BM25 as retriever
        - Elastic search as vector database
    """
    def __init__(
            self, provider: ProviderService, 
            rag_config: RAGConfig,
            update_notification_func):
        """
            Initialize the RAG
           
            @param rag_config RAGConfig
            @param provider ProviderService
        """
        self.retrieve_parent_document = None
        self.rag_config = rag_config
        self.database = provider.get_docstore()
        self.index_doc = self.database.find_document(category=rag_config.db_category, id="index")
        self.provider = provider
        if self.index_doc != None:
            print("loaded index doc") 

        self.log = AppLogService(f"hybrid_gemini_rag-{self.rag_config.db_category}.log")
        self.update_notification_func = update_notification_func 
        # Build chain
        chat_model = provider.get_gemini_pro(convert_system_message=False)
        self.gemini = provider.get_simple_gemini_pro()
        prompt = ChatPromptTemplate.from_template(TEMPLATE)
        self.__init_retriever(provider=provider)
        self.chain = (
            {"context": itemgetter("question") | RunnableLambda(self.ensemble_retriever.invoke), 
             "question": itemgetter("question")
            }
            | RunnableLambda(self.__filter_format_doc)
            | prompt
            | chat_model
            | RunnableLambda(self.__update_format_answer)
        ) 
        return

    def __filter_format_doc(self, input_dict):
        """
            Note! for internal class use only.

            This method formats the retrieved documnents from the retriever.
            It helps the chat model understands the context better.
        """
        question = input_dict['question']

        # filter similar doc_id
        id_list = {}
        for d in input_dict['context']:
            id = d.metadata['id']
            if id in id_list:
                continue
            id_list[id] = 1

        parent_docs = [
            self.database.find_document(category=self.rag_config.db_category, id=id) for id in id_list.keys()]
        
        # answer docs
        answer_list_str = self.__answer_documents_parallel(question=question, docs=parent_docs)
        answer_str = "\n- "+"\n- ".join(answer_list_str)
        
        stuff_data = f"# Your specific knowledge for '{question}':\n{answer_str}\n"
        stuff_data += f"# Your general knowledge:\n{self.index_doc.content}\n"

        input_dict['context'] = stuff_data
        self.retrieve_parent_document = self.index_doc
        return input_dict
    
    def __answer_documents(self, question: str, docs: List[TDTDoc]) -> List[str]:
        prompt = ChatPromptTemplate.from_template(TEMPLATE)
        chain = prompt | self.gemini
        answers = []
        for doc in docs:
            try:
                resp = chain.invoke({"question": question, "context": doc.content})
                answers.append(resp)
            except:
                self.log.logger.error("Can't answer")
        return answers

    def __answer_documents_parallel(self, question: str, docs: List[TDTDoc]) -> List[str]:
        chains = {}
        inputs = []
        for idx, d in enumerate(docs):
            template = TEMPLATE.replace("{context}", d.content)
            llm_chain = PromptTemplate.from_template(template=template) | self.provider.get_simple_gemini_pro()
            # chains.append(llm_chain)
            chains[str(idx)] = llm_chain
            inputs.append(question)
        map_chain = RunnableParallel(**chains)
        try:
            map_answers = map_chain.invoke({"question": question})
        except Exception:
            map_answers = {'1': 'None'}
            self.log.logger.exception(Exception)
        answers = list(map_answers.values())
        return answers

    def __update_format_answer(self, answer):
        """
            Note! for internal class use only.

            This method formats the retrieved documnents from the retriever.
            It helps the chat model understands the context better.
        """
        resp = RAGResponse(
            answer=answer.content.strip(), 
            category=self.rag_config.db_category,
            document=self.retrieve_parent_document)
        return resp

    @traceable(tags=['hybrid_gemini'])
    def ask_rag(self, question: str) -> RAGResponse:
        """
            Ask the RAG a question.
            @param question
            @return answer, 'None' if it can't
        """
        try:
            answer = self.chain.invoke({"question": question})
        except Exception:
            self.log.logger.exception(msg="can't answer RAG")
            return None
        return answer

    def __init_retriever(self, provider: ProviderService):
        """
            Note! for internal use only.

            Initialize Elastic, BM25 instances and combine them into hybrid search
            This method is intented for private use. Please be cautious modifying.
        """
        K = 2
        # elastic
        es_connect = provider.load_elasticsearch_connection()
        es = provider.get_elasticsearch_store(
            index=self.rag_config.vector_index, 
            embed_type=self.rag_config.embed_model)
        es_retriever = es.as_retriever(search_kwargs={"k": K, "fetch_k": 10})
        es_retriever = es.as_retriever()
        self.es = es_retriever
        # BM-25
        bm25_retriever = MyElasticSearchBM25Retriever(client=es_connect, index_name=self.rag_config.text_index)
        bm25_retriever.k = K
        self.bm25 = bm25_retriever
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, es_retriever],
            weights=[0.4, 0.6])
        return 