from langchain_community.vectorstores.elasticsearch import ElasticsearchStore
from langchain.retrievers import EnsembleRetriever
from langchain_core.output_parsers import StrOutputParser
from langsmith.run_helpers import traceable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from operator import itemgetter
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
Hãy hỗ trợ thật tốt với yêu cầu sau đến từ người dùng. Output "None" if you cannot answer.
Yêu cầu: {question}
"""


class HybridGeminiRAG:
    """
        This is a RAG designed to search docs in vector store and provide answers to user.
        It uses:
        - Gemini as chat model
        - LaBSE + BM25 as retriever
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
        self.log = AppLogService(f"hybrid_gemini_rag-{self.rag_config.db_category}.log")
        # Filter chain
        self.filter_chain = self.__build_filter_chain(provider=provider)
        # Build chain
        chat_model = provider.get_gemini_pro(convert_system_message=False)
        prompt = ChatPromptTemplate.from_template(TEMPLATE)
        self.__init_retriever(provider=provider)
        self.chain = (
            {"context": itemgetter("question") | self.ensemble_retriever, 
             "question": itemgetter("question")
            }
            | RunnableLambda(self.__filter_format_doc)
            | prompt
            | chat_model
            | StrOutputParser()
            | RunnableLambda(update_notification_func)
            | RunnableLambda(self.__format_answer)
        ) 
        return
    
    def __build_filter_chain(self, provider: ProviderService):
        """
            Build a filter chain to filter relevant retrieved documents to user query.
        """
        template = "Is this question '{question}' relevant to '{title}'. Output yes or no."
        prompt = ChatPromptTemplate.from_template(template=template)
        chain = ({
            "question": itemgetter("question"),
            "title": itemgetter("title")
        }
        | prompt
        | provider.get_gemini_pro()
        | StrOutputParser())
        return chain

    def __filter_format_doc(self, input_dict):
        """
            Note! for internal class use only.

            This method formats the retrieved documnents from the retriever.
            It helps the chat model understands the context better.
        """
        correct_doc = None
        retrieve_docs = input_dict['context']
        for retrieve_doc in retrieve_docs:
            doc_id = retrieve_doc.metadata['id']
            document = self.database.find_document(category=self.rag_config.db_category, id=doc_id)
            filter = self.filter_chain.invoke({"question": input_dict['question'], "title": document.title})
            correct_doc = document
            if filter.lower() == 'yes':
                break
        input_dict['context'] = correct_doc.content
        self.retrieve_parent_document = correct_doc
        return input_dict
    
    def __format_answer(self, answer):
        """
            Note! for internal class use only.

            This method formats the retrieved documnents from the retriever.
            It helps the chat model understands the context better.
        """
        resp = RAGResponse(
            answer=answer.strip(), 
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
        embeddings = provider.get_hf_api_embeddings(self.rag_config.embed_model)
        # elastic
        es_connect = provider.load_elasticsearch_connection()
        es = ElasticsearchStore(
            es_connection=es_connect,
            embedding=embeddings,
            index_name=self.rag_config.vector_index, 
            distance_strategy="EUCLIDEAN_DISTANCE") 
        es_retriever = es.as_retriever(search_kwargs={"k": 1})
        self.es = es_retriever
        # BM-25
        bm25_retriever = MyElasticSearchBM25Retriever(client=es_connect, index_name=self.rag_config.text_index)
        bm25_retriever.k = 1
        self.bm25 = bm25_retriever
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, es_retriever],
            weights=[0.5, 0.5])
        return 