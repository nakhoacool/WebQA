import os
from typing import List
import firebase_admin
from firebase_admin import credentials

class ConfigurationService:
    """
        A service designed to load secret keys, API keys...
    """
    def __init__(self):
        self.env_path = os.path.dirname(__file__)
        self.path = f"{self.env_path}/../../.keys"
        return

    def load_hg_token(self, nth:int = 0) -> str:
        """
            load hugging face token from a pool of token.
            @param nth the nth key you need to load

            @return the token
        """
        with open(self.path+"/hg_keys") as f:
            key = f.readlines()
        return key[nth].strip()

    def init_firebase_connection(self):
        cred = credentials.Certificate(self.path+'/firebaseAccountKey.json')
        return firebase_admin.initialize_app(cred)

    def load_langsmith_token(self) -> str:
        """
            load langsmith token.
            
            @return the token
        """
        with open(self.path+"/langsmith") as f:
            key = f.read()
        return key.strip()
 
    def load_openai_token(self) -> str:
        """
            load OpenAI token

            @return the token
        """
        with open(self.path+"/openai") as f:
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

    def load_elasticsearch_config(self):
        """
            load elastic search configuration

            @return an array of size 3
            1. the nodes
            2. the auth
            3. ca_cert
        """
        with open(f"{self.path}/elastic.nodes") as f:
            nodes = f.readlines()
        with open(f"{self.path}/elastic.auth") as f:
            auth = f.read().strip().split(":")
        ca_cert = f'{self.path}/ca.crt'
        return nodes, auth, ca_cert