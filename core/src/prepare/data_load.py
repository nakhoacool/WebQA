import pandas as pd
from collections import Counter
import os
from typing import List, Dict
from langchain_core.documents.base import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.prepare.types import TDTDoc

class DocDataLoader:

    """
        This class responsible for loading csv data to collection of documents.
    """

    def __init__(self):
        self.env_path = os.path.dirname(__file__)
        self.word_len_func = lambda e: len(e.split(" "))
        pass

    def load_major_docs(self, size:int = 1600, overlap:int = 100) -> List[Document]:
        """
            This method loads major blog post data into documents.
            @param size chunk_size
            @param overlap overlap_size

            @return a list of documents
        """
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n\n","\n\n", "\n"],
            chunk_size=size, chunk_overlap=overlap, 
            length_function=self.word_len_func, is_separator_regex=False
        )
        db_df = pd.read_csv(f'{self.env_path}/../../data/test_major/docs.csv')
        dist = []
        db = []
        for i, data in db_df.iterrows():
            doc = text_splitter.create_documents([data['content']])
            dist.append(len(doc))
            [d.metadata.update({"id": data['id']}) for d in doc]
            db.extend(doc)
        print(f"From {db_df.shape} to {Counter(dist)}")
        return db
    
    def load_major_docs_full(self) -> List[Document]:
        """
            This method loads major blog post data into documents AS A WHOLE.
        
            @return a list of documents
        """
        db_df = pd.read_csv(f'{self.env_path}/../../data/test_major/docs.csv')
        db = []
        for i, data in db_df.iterrows():
            doc = Document(page_content=data['content'], metadata={"id": data['id']})
            db.append(doc)
        print(f"From {db_df.shape} to {len(db)}")
        return db
    
    def load_major_docs_full_asmap(self) -> Dict[int, TDTDoc]:
        """
            This method loads major blog post data into documents AS A WHOLE.
        
            @return a dict of id, documents
        """
        db_df = pd.read_csv(f'{self.env_path}/../../data/db/majors_info.csv')
        db = {}
        for i, data in db_df.iterrows():
            db[data['id']] = TDTDoc(content=data['content'], src=data['source'], id=int(data['id']), title=data['title'])
        print(f"From {db_df.shape} to {len(db)}")
        return db