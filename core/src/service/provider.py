from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from elasticsearch import Elasticsearch
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from src.service.config import ConfigurationService
from src.service.docstore import DocStore, DocCategories

class ProviderService:

    def __init__(self) -> None:
        self.config = ConfigurationService()
        self.docstore = DocStore()
        self.categories = DocCategories()
        pass

    def get_docstore(self) -> DocStore:
        """
            get an instance of DocStore, a database to all the documents
        """
        return self.docstore
    
    def get_categories(self) -> DocCategories:
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
    
    def get_gemini_pro(self, convert_system_message:bool) -> ChatGoogleGenerativeAI:
        """
            get an instance of gemini pro

            @return gemini chat model
        """
        chat_model = ChatGoogleGenerativeAI(
            model="gemini-pro", 
            temperature=0, 
            google_api_key=self.config.load_gemini_token(),
            convert_system_message_to_human=convert_system_message
        )
        return chat_model
    
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