from src.rag.hybrid_gemini import HybridGeminiRag
from src.rag.types import RAGResponse
from src.config import Configuration

class MasterBot:

    def __init__(self) -> None:
        self.conf = Configuration()
        self.major_rag = HybridGeminiRag(
            es_index="labse-major", 
            embed_model="sentence-transformers/LaBSE", 
            config=self.conf)
        return


    def ask_rags(self, question:str) -> RAGResponse:
        """
            Update soon!
            This method select the propriate RAG and run it.
        """
        resp = self.major_rag.ask_rag(question=question)
        return resp