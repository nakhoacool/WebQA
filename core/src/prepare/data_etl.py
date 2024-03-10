import pandas as pd
from collections import Counter
import os
from typing import List, Dict
from langchain_core.documents.base import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.prepare.types import TDTDoc
from src.service.provider import ProviderService
from src.rag.types import RAGConfig
from uuid import uuid4

class DataETL:
    """
        This class responsible for loading csv data to collection of documents.
    """
    def __init__(self, provider: ProviderService, rag_config: RAGConfig):
        """
            Initialize an instance
        """
        self.env_path = os.path.dirname(__file__)
        self.fire = provider.get_firebase()
        self.config = rag_config
        self.es = provider.get_elasticsearch_store(
            index=rag_config.vector_index, 
            embed_type=rag_config.embed_model)
        self.bm25 = provider.get_elasticsearch_bm25(index=rag_config.text_index)
        self.index_page = ""
        return

    def create_splitter(self, chunk_size: int = 460, overlap: int = 20) -> RecursiveCharacterTextSplitter:
        """
            get an instance of a text splitter
        """
        word_len_func = lambda e: len(e.split(" "))

        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n\n","\n\n", "\n"],
            chunk_size=chunk_size, chunk_overlap=overlap, 
            length_function=word_len_func, is_separator_regex=False
        )
        return text_splitter

    def try_split_text(self, data_folder:str, size:int = 460, overlap:int = 20) -> List[Document]:
        """
            This method loads data into split documents.
            @param data_folder the name of the data folder
            @param size chunk_size
            @param overlap overlap_size

            @return a list of documents
        """
        text_splitter = self.create_splitter(chunk_size=size, overlap=overlap)
        db_df = pd.read_csv(f'{self.env_path}/../../data/{data_folder}/docs.csv')
        dist = []
        db = []
        for i, data in db_df.iterrows():
            doc = text_splitter.create_documents([data['content']])
            dist.append(len(doc))
            [d.metadata.update({"id": data['id']}) for d in doc]
            db.extend(doc)
        print(f"From {db_df.shape} to {Counter(dist)}")
        return db

    def upload_df_docs(self, data_folder:str, size:int = 460, overlap:int = 20) -> List[TDTDoc]:
        """
            This method loads data into split documents.
            @param data_folder the name of the data folder
            @param size chunk_size
            @param overlap overlap_size

            @return a list of documents
        """
        results = []
        db_df = pd.read_csv(f'{self.env_path}/../../data/{data_folder}/docs.csv')
        text_splitter = self.create_splitter(chunk_size=size, overlap=overlap)
        for i, data in db_df.iterrows():
            tmp_doc = self.upload_doc(
                data=data.to_dict(), 
                text_splitter=text_splitter)
            results.append(tmp_doc)
            # update index page
            self.index_page += f"{tmp_doc.title}: {tmp_doc.content[:20]}...\n"
        tmp_idx = self.upload_index_page(index_page=self.index_page)
        results.append(tmp_idx)
        print("DONE")
        return results

    def upload_index_page(self, index_page: str):
        index_doc = TDTDoc(content=index_page, src="index.html", id="index", title="Bảng mục lục")
        self.fire.update_document(collection=self.config.db_category, document_id="index", update_document=index_doc)
        print("-> Update index doc")
        return index_doc

    def upload_doc(self, data, text_splitter) -> TDTDoc:
        """
            Upload a single document    
        
            @param data: {
                "content": str,
                "source": str,
                "title": str
            }
        """
        parent_id = str(uuid4())
        # upload to elastic
        split_docs = text_splitter.create_documents([data['content']])
        [d.metadata.update({"id": parent_id}) for d in split_docs]
        vec_child_ids = self.es.add_documents(documents=split_docs)
        txt_child_ids = self.bm25.add_documents(documents=split_docs)
        print(f"-> DONE: upload to elastic search {len(vec_child_ids)} & {len(txt_child_ids)} docs")
        # upload to firebase
        firebase_doc = TDTDoc(content=data['content'], src=data['source'], id=parent_id, title=data['title'])
        firebase_doc.set_vector_child_ids(vec_child_ids)
        firebase_doc.set_text_child_ids(txt_child_ids)
        self.fire.create_document(self.config.db_category, firebase_doc.id, document_data=firebase_doc)
        print(f"-> DONE: upload to firebase at {self.config.db_category}")
        return firebase_doc

    def delete_doc(self, doc: TDTDoc):
        if doc.txt_child_ids == None and doc.vec_child_ids == None:
            print("Not publish yet")
            return
        self.es.delete(ids=doc.vec_child_ids)
        self.bm25.delete_document(document_ids=doc.txt_child_ids)
        self.fire.delete_document(collection=self.config.db_category, document_id=doc.id)
        return
    
    def update_doc(self, doc: TDTDoc):
        if doc.txt_child_ids == None and doc.vec_child_ids == None:
            print("Not publish yet")
            return
        self.delete_doc(doc)
        self.update_doc(doc)
        return
    
