from langchain.chains import HypotheticalDocumentEmbedder 
from src.service.provider import ProviderService
from typing import Tuple, List
from langchain_core.documents import Document
from src.custom.es_bm25_retriever import MyElasticSearchBM25Retriever
from langchain.retrievers import EnsembleRetriever
from src.utils.config_utils import RAGConfig
from src.service.applog import AppLogService
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough


TEMPLATE = """Bạn là một người tư vấn viên thân thiện và đầy hiểu biết. Nhiệm vụ của bạn là hỗ trợ người dùng hiểu biết hơn về trường đại học Tôn Đức Thắng.

Hãy kết hợp kiến thức của bạn và đọc thật kỹ các dữ liệu dưới đây để trả lời câu hỏi:
```
{context}
```
Câu hỏi: {question}?

Hãy trả lời một cách thật hữu ích, ngắn gọn, xúc tích, cấu trúc câu đầy đủ. Output "None" if you cannot answer
"""

SEPERATOR = "# Dữ liệu"

class HydeRAG:

    def __init__(self, provider: ProviderService, index: str, k: int = 4) -> None:
        self.es = provider.get_elasticsearch_store(index=index)
        self.gemini = provider.get_simple_gemini_pro()
        self.base_emdeddings = provider.get_gemini_embeddings()
        self.embeddings = HypotheticalDocumentEmbedder.from_llm(self.gemini, self.base_emdeddings, "web_search")
        self.k = k
        self.errors = []
        self.log = AppLogService(f"hyde-rag-{index}.log")
        return
    
    def search(self, question:str) -> List[Tuple[Document, float]]:
        hyde_doc = None
        try:
            hyde_doc = self.embeddings.invoke(question)
        except Exception:
            self.log.logger.exception(msg=f"[can't answer RAG] {question}")
            return None
        if(hyde_doc == None or len(hyde_doc['text']) <= 0):
            self.errors.append(question)
            return None
        docs = self.es.similarity_search_with_relevance_scores(query=hyde_doc['text'], k=self.k)
        return docs
    

class HydeHybridSearchRAG:

    def __init__(self, provider: ProviderService, config: RAGConfig, k: int = 4) -> None:
        self.k = k
        self.rag_config = config
        self.ensemble_retriever = self.__init_retriever(provider=provider)
        self.gemini = provider.get_simple_gemini_pro("gemini-1.5-flash-latest")
        self.base_emdeddings = provider.get_gemini_embeddings()
        self.embeddings = HypotheticalDocumentEmbedder.from_llm(self.gemini, self.base_emdeddings, "web_search")
        self.log = AppLogService(f"hyde-hybrid-rag-{config.vector_index}.log")
        self.retrieve_docs = []
        self.chain = self.__build_chain()
        return
    
    def search(self, question:str) -> List[Tuple[Document, float]]:
        hyde_doc = None
        try:
            hyde_doc = self.embeddings.invoke(question)
        except Exception:
            self.log.logger.exception(msg=f"[can't answer RAG] {question}")
            return None
        if(hyde_doc == None or len(hyde_doc['text']) <= 0):
            return None
        docs = self.ensemble_retriever.invoke(hyde_doc["text"])
        return docs
    
    def answer(self, question: str) -> str:
        ans = ''
        try:
            hyde_doc = self.embeddings.invoke(question)
            hyde_ques = hyde_doc['text']
            if hyde_ques is None or len(hyde_ques) <= 0:
                return ""
            ans = self.chain.invoke(hyde_ques)
        except Exception:
            self.log.logger.exception(msg=f"[NO ANSWER] {question}")
            return ""
        return ans
    
    def __init_retriever(self, provider: ProviderService):
        """
            Note! for internal use only.

            Initialize Elastic, BM25 instances and combine them into hybrid search
            This method is intented for private use. Please be cautious modifying.
        """
        # elastic
        es_connect = provider.load_elasticsearch_connection()
        es = provider.get_elasticsearch_store(
            index=self.rag_config.vector_index, 
            embed_type=self.rag_config.embed_model)
        es_retriever = es.as_retriever(search_kwargs={"k": self.k, "fetch_k": 10})
        self.es = es_retriever
        # BM-25
        bm25_retriever = MyElasticSearchBM25Retriever(client=es_connect, index_name=self.rag_config.text_index)
        bm25_retriever.k = self.k
        self.bm25 = bm25_retriever
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, es_retriever],
            weights=[0.5, 0.5])
        return ensemble_retriever
    
    def __build_chain(self):
        """
            Note! private method

            Initialize the RAG chain.
        """
        prompt = PromptTemplate.from_template(template=TEMPLATE)
        rag = (
            {"context": self.ensemble_retriever | self.__store_docs | self.__format_doc,
                 "question": RunnablePassthrough()} | prompt | self.gemini)
        return rag

    def __format_doc(self, docs: List[Document]):
        """
            Note! private method

            Prepare list of docs into a single string
        """
        doc_str = ""
        for idx, d in enumerate(docs):
            doc_str = f"{doc_str}\n {SEPERATOR} {idx+1}:\n{d.page_content}\n"
        return doc_str

    def __store_docs(self, docs):
        """
            Note! private method

            Store the retrieved documents to a list.
        """
        self.retrieve_docs.append(docs)
        return docs