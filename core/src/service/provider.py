from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from elasticsearch import Elasticsearch
from langchain_community.chat_models import ChatOpenAI
from langchain_community.vectorstores.elasticsearch import ElasticsearchStore
from langchain_community.llms.openai import OpenAI
from langchain_google_genai import GoogleGenerativeAI, ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from src.service.config import ConfigurationService
from src.retreiver.firebase_store import FirebaseStore
from src.rag.types import RAGCategories
from src.retreiver.es_bm25_retriever import MyElasticSearchBM25Retriever
from langchain_openai import OpenAIEmbeddings

class ProviderService:

    def __init__(self) -> None:
        self.config = ConfigurationService()
        self.docstore = FirebaseStore(config=self.config)
        self.categories = RAGCategories()
        # self.webloader = WebPageMDLoader()
        return


    def get_firebase(self) -> FirebaseStore:
        """
            get an instance of Firebase retriever
        """
        return self.docstore

    def get_docstore(self) -> FirebaseStore:
        """
            get an instance of DocStore, a database to all the documents
        """
        return self.docstore
    
    def get_categories(self) -> RAGCategories:
        return self.categories

    def load_elasticsearch_connection(self) -> Elasticsearch:
        """
            load elastic search connection from hosted cloud

            @return a es connection
        """
        nodes, auth, ca_certs = self.config.load_elasticsearch_config() 
        es = Elasticsearch(
            nodes, 
            basic_auth=auth, 
            ca_certs=ca_certs)
        return es
    
    def get_gemini_pro(self, convert_system_message:bool = False) -> ChatGoogleGenerativeAI:
        """
            get an instance of gemini pro chat model

            @return gemini chat model
        """
        chat_model = ChatGoogleGenerativeAI(
            model="gemini-pro", 
            temperature=0, 
            google_api_key=self.config.load_gemini_token(),
            convert_system_message_to_human=convert_system_message
        )
        return chat_model
    
    def get_simple_gemini_pro(self) -> GoogleGenerativeAI:
        """
            get an instance of gemini model

            @return gemini model
        """
        model = GoogleGenerativeAI(
            model="gemini-pro", 
            temperature=0, google_api_key=self.config.load_gemini_token())
        return model
    
    def get_chat_openai(self):
        """
            get an instance of OpenAI chat model

            @return a chat model
        """
        model = ChatOpenAI(
            temperature=0,
            max_tokens=1800,
            openai_api_key=self.config.load_openai_token())
        return model
    
    def get_openai(self):
        """
            get an instance of OpenAI model

            @return model
        """
        model = OpenAI(temperature=0, max_tokens=1800, openai_api_key=self.config.load_openai_token())
        return model

    def get_gemini_embeddings(self) -> GoogleGenerativeAIEmbeddings:
        """
            get an instance of gemini embedding model

            @return embedding model
        """
        model = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", 
            google_api_key=self.config.load_gemini_token())
        return model
    
    def get_hf_api_embeddings(self, embed_model:str) -> HuggingFaceInferenceAPIEmbeddings:
        """
            get Hugging Face embedding model
        """
        if embed_model == None or embed_model == "":
            embed_model = "sentence-transformers/LaBSE"
        embeddings = HuggingFaceInferenceAPIEmbeddings(
            model_name=embed_model, api_key=self.config.load_hg_token())
        return embeddings


    def get_openai_embeddings(self, embed_model:str = "text-embedding-3-small") -> OpenAIEmbeddings:
        """
            get open ai embedding model
        """
        embeddings = OpenAIEmbeddings(model=embed_model,api_key=self.config.load_openai_token())
        return embeddings
    

    def get_elasticsearch_store(self, index:str, embed_type:str="gemini", dist:str="EUCLIDEAN_DISTANCE") -> ElasticsearchStore:
        """
            get elastic search with model

            @param embed_type model provider: hg (hugging face), gemini, openai
        """
        embed = None
        if embed_type == "hg":
            embed = self.get_hf_api_embeddings()
        elif embed_type == "openai":
            embed = self.get_openai_embeddings()
        else:
            embed = self.get_gemini_embeddings()

        es = ElasticsearchStore(
            es_connection=self.load_elasticsearch_connection(),
            embedding=embed,
            index_name=index, 
            distance_strategy=dist)
        return es
    

    def get_elasticsearch_bm25(self, index: str) -> MyElasticSearchBM25Retriever:
        """
            get elastic search with BM25

            @param index index name
        """
        bm25_retriever = MyElasticSearchBM25Retriever(
            client=self.load_elasticsearch_connection(), 
            index_name=index)
        return bm25_retriever