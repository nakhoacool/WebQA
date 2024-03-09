from typing import Dict
from langchain_core.documents.base import Document

class TDTDoc:

    def __init__(self, content: str = "", src: str = "", id: str = "", title: str = "") -> None:
        self.content = content
        self.source = src
        self.id = id
        self.title = title
        return

    def set_content(self, content: str):
        if content == None or len(content) == 0:
            return
        self.content = content
        return

    def to_json(self) -> Dict:
        data = {
            "id": self.id,
            "content": self.content,
            "title": self.title,
            "source": self.source
        }
        return data
    
    def from_json(self, data: Dict):
        self.id = data['id']
        self.content = data['content']
        self.source = data['source']
        self.title = data['title']
        return
    

class FirebaseTDTDoc:

    def __init__(self, doc: TDTDoc) -> None:
        self.doc = doc
        self.vec_child_ids = []
        self.txt_child_ids = []
        return

    def to_json(self) -> Dict:
        data = {
            "id": self.doc.id,
            "content": self.doc.content,
            "title": self.doc.title,
            "source": self.doc.source,
            "vec_child_ids": self.vec_child_ids,
            "txt_child_ids": self.txt_child_ids
        }
        return data
    
    def from_json(self, data: Dict):
        doc = TDTDoc()
        doc.content = data['content']
        doc.title = data['title']
        doc.id = data['id']
        doc.source = data['source']
        self.doc = doc
        self.txt_child_ids = data['txt_child_ids']
        self.vec_child_ids = data['vec_child_ids']
        return
