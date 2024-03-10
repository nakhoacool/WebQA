from typing import Dict, List
from langchain_core.documents.base import Document

class TDTDoc:

    def __init__(self, content: str = "", src: str = "", id: str = "", title: str = "") -> None:
        self.content = content
        self.source = src
        self.id = id
        self.title = title
        self.vec_child_ids = None
        self.txt_child_ids = None
        return
    
    def set_text_child_ids(self, ids: List[str]):
        if self.txt_child_ids == None:
            self.txt_child_ids = []
        self.txt_child_ids = ids
        return

    def set_vector_child_ids(self, ids: List[str]):
        if self.vec_child_ids == None:
            self.vec_child_ids = []
        self.vec_child_ids = ids
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
            "source": self.source,
            "vec_child_ids": self.vec_child_ids,
            "txt_child_ids": self.txt_child_ids
        }
        return data
    
    def from_json(self, data: Dict):
        self.id = data['id']
        self.content = data['content']
        self.source = data['source']
        self.title = data['title']
        self.set_text_child_ids(data['txt_child_ids'])
        self.set_vector_child_ids(data['vec_child_ids'])
        return