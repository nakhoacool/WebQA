from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_community.vectorstores.elasticsearch import ElasticsearchStore
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain_core.output_parsers import StrOutputParser
from langsmith.run_helpers import traceable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from src.config import Configuration
from src.prepare.data_load import DocDataLoader

class HybridGeminiRag:
    """
        Formula: RAG = Gemini + ES + Hybrid Search
        Features:
        - Vector Store Memory
    """

    def __init__(self, es_index: str, embed_model: str, config: Configuration):
        """
            Initialize the RAG
            @param es_index elastic search index
            @param embed_model hugging face sentence-transformer model
            @param config Configuration
        """
        self.chat_model = ChatGoogleGenerativeAI(
            model="gemini-pro", 
            temperature=0, 
            google_api_key=config.load_gemini_token()
        )
        template = """\
            Answer the question based only on the following context: \
                {context} \
            Question: {question}"""
        prompt = ChatPromptTemplate.from_template(template)
        self._init_retriever(es_index=es_index, embed_model=embed_model, config=config)
        self.rag = (
            {"context": self.ensemble_retriever, "question": RunnablePassthrough()}
            | prompt
            | self.chat_model
            | StrOutputParser()
        ) 
        return
    
    @traceable(tags=['hybrid_gemini'])
    def ask_rag(self, question: str) -> str:
        """
            Ask the RAG a question.
            @param question

            @return answer
        """
        if question == None:
            return "No question was asked"
        answer = self.rag.invoke(question)
        return answer.strip()

    def _init_retriever(self, es_index:str, embed_model:str, config:Configuration):
        """
            Initialize Elastic, BM25 instances and combine them into hybrid search
            This method is intented for private use. Please be cautious modifying.
        """
        embeddings = HuggingFaceInferenceAPIEmbeddings(
            model_name=embed_model, api_key=config.load_hg_token())
        # elastic
        es = ElasticsearchStore(
            es_connection=config.load_elasticsearch_connection(),
            embedding=embeddings,
            index_name=es_index, distance_strategy="EUCLIDEAN_DISTANCE") 
        self.es_retriever = es.as_retriever(search_kwargs={"k": 2})
        # BM-25
        doc_loader = DocDataLoader()
        self.bm25_retriever = BM25Retriever.from_documents(doc_loader.load_major_docs())
        self.bm25_retriever.k = 2
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[self.bm25_retriever, self.es_retriever],
            weights=[0.5, 0.5])
        del doc_loader
        return self.ensemble_retriever