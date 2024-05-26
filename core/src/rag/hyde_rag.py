from langchain.chains import HypotheticalDocumentEmbedder, LLMChain
from src.service.provider import ProviderService
from typing import Tuple, List
from langchain_core.documents import Document

class HydeRAG:

    def __init__(self, provider: ProviderService, index: str, k: int = 4) -> None:
        self.es = provider.get_elasticsearch_store(index=index)
        self.gemini = provider.get_simple_gemini_pro()
        self.base_emdeddings = provider.get_gemini_embeddings()
        self.embeddings = HypotheticalDocumentEmbedder.from_llm(self.gemini, self.base_emdeddings, "web_search")
        self.k = k
        return
    
    def search(self, question:str) -> List[Tuple[Document, float]]:
        hyde_doc = self.embeddings.invoke(question)
        docs = self.es.similarity_search_with_relevance_scores(query=hyde_doc['text'], k=self.k)
        return docs