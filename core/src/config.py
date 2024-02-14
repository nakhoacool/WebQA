import os
from elasticsearch import Elasticsearch
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

class Configuration:
    """
        This class responsible for loading API key, ES connection, LLM
    """

    def __init__(self):
        self.env_path = os.path.dirname(__file__)
        self.path = f"{self.env_path}/../.keys"

    def load_hg_token(self, nth:int = 0) -> str:
        """
            load hugging face token from a pool of token.
            @param nth the nth key you need to load

            @return the token
        """
        with open(self.path+"/hg_keys") as f:
            key = f.readlines()
        return key[nth].strip()

    def load_langsmith_token(self) -> str:
        """
            load langsmith token.
            
            @return the token
        """
        with open(self.path+"/langsmith") as f:
            key = f.read()
        return key.strip()
 
    def load_gemini_token(self) -> str:
        """
            load google gemini API token

            @return the token
        """
        with open(self.path+"/gemini") as f:
            key = f.read()
        return key.strip()

    def load_tavily_token(self):
        """
            load tavily API token
            @return the token
        """
        with open(self.path+"/tavily") as f:
            key = f.read()
        return key.strip()

    def set_tavily_token(self):
        token = self.load_tavily_token()
        os.environ["TAVILY_API_KEY"] = token
        return

    def enable_tracing(self, project:str):
        """
            enable tracing on langsmith.
            @param project the name of the langsmith project
        """
        os.environ["LANGCHAIN_TRACING_V2"]="true"
        os.environ["LANGCHAIN_ENDPOINT"]="https://api.smith.langchain.com"
        os.environ["LANGCHAIN_API_KEY"]=self.load_langsmith_token()
        os.environ["LANGCHAIN_PROJECT"]=project.strip()
        return

    def load_elasticsearch_connection(self) -> Elasticsearch:
        """
            load elastic search connection from hosted cloud

            @return a es connection
        """
        with open(f"{self.env_path}/../.keys/elastic.nodes") as f:
            nodes = f.readlines()
        with open(f"{self.env_path}/../.keys/elastic.auth") as f:
            auth = f.read().strip().split(":")
        es = Elasticsearch(
            nodes, 
            basic_auth=auth, 
            ca_certs=f'{self.env_path}/../.keys/ca.crt')
        return es
    
    def get_gemini_pro(self, convert_system_message:bool) -> ChatGoogleGenerativeAI:
        """
            get an instance of gemini pro

            @return gemini chat model
        """
        chat_model = ChatGoogleGenerativeAI(
            model="gemini-pro", 
            temperature=0, 
            google_api_key=self.load_gemini_token(),
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
            google_api_key=self.load_gemini_token())
        return model
