from langchain.chains import HypotheticalDocumentEmbedder 
from src.service.provider import ProviderService
from typing import Tuple, List
from langchain_core.documents import Document
from src.custom.es_bm25_retriever import MyElasticSearchBM25Retriever
from langchain.retrievers import EnsembleRetriever
from src.utils.config_utils import RAGConfig
from src.service.applog import AppLogService

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
        self.__init_retriever(provider=provider)
        self.gemini = provider.get_simple_gemini_pro()
        self.base_emdeddings = provider.get_gemini_embeddings()
        self.embeddings = HypotheticalDocumentEmbedder.from_llm(self.gemini, self.base_emdeddings, "web_search")
        self.log = AppLogService(f"hyde-hybrid-rag-{config.vector_index}.log")
        self.errors = []
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
        docs = self.ensemble_retriever.invoke(hyde_doc["text"])
        return docs
    
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
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, es_retriever],
            weights=[0.5, 0.5])
        return 