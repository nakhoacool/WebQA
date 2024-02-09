from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_community.vectorstores.elasticsearch import ElasticsearchStore
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain_core.output_parsers import StrOutputParser
from langsmith.run_helpers import traceable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from operator import itemgetter
import uuid
from src.config import Configuration
from src.prepare.data_load import DocDataLoader
from src.rag.types import RAGResponse, RAGCategories

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
        self.ask_memory = {}
        template = ""
        template += "You are a helpful admission assistant for Ton Duc Thang university who gives helpful and accurate information.\n"
        template += 'Answer the question mainly using the following context. Output "None" if you cannot answer:'
        template += "\n```\n{context}\n```\n"
        template += "Question: {question}\n"
        prompt = ChatPromptTemplate.from_template(template)
        self._init_retriever(es_index=es_index, embed_model=embed_model, config=config)
        self.rag = (
            {"context": itemgetter("question") | self.ensemble_retriever, 
             "question": itemgetter("question"), "ask_id": itemgetter("ask_id")}
            | RunnableLambda(self._format_doc)
            | prompt
            | self.chat_model
            | StrOutputParser()
        ) 
        return
    
    def _format_doc(self, input_dict):
        data = {**input_dict}
        retrieve_doc = input_dict['context'][0]
        doc_id = retrieve_doc.metadata['id']
        document = self.database[doc_id]
        data['content'] = document.content
        # store to a temporary mem
        self.ask_memory[input_dict['ask_id']] = document
        return data

    @traceable(tags=['hybrid_gemini'])
    def ask_rag(self, question: str) -> RAGResponse:
        """
            Ask the RAG a question.
            @param question

            @return answer, 'None' if it can't
        """
        ask_id = uuid.uuid1().int
        if question == None:
            return "No question was asked"
        if ask_id == None:
            return "Went wrong. Cannot generate uuid"
        answer = self.rag.invoke({"question": question, "ask_id": ask_id})
        status = 200
        if answer.lower() == "none":
            status = 404
        resp = RAGResponse(
            answer=answer.strip(), 
            status=status, 
            category=RAGCategories.major, 
            document=self.ask_memory.pop(ask_id))
        return resp

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
        self.es_retriever = es.as_retriever(search_kwargs={"k": 1})
        # BM-25
        doc_loader = DocDataLoader()
        db = doc_loader.load_major_docs(size=460, overlap=20)
        self.database = doc_loader.load_major_docs_full_asmap()
        self.bm25_retriever = BM25Retriever.from_documents(db)
        self.bm25_retriever.k = 1
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[self.bm25_retriever, self.es_retriever],
            weights=[0.5, 0.5])
        del doc_loader
        return 
