from typing import Dict, List
from langchain_core.documents import Document
from typing import TypedDict, List

class ConfigParentRAG(TypedDict):
    vec_index: str
    txt_index: str
    vec_weight: float = 0.5
    txt_weight: float = 0.5
    total_k: int = 4
    llm: str = 'gemini-1.5-flash'

def get_default_config() -> ConfigParentRAG:
    config: ConfigParentRAG = {}
    config['llm'] = "gemini-1.5-flash"
    config['total_k'] = 4
    config['txt_weight'] = .5
    config['vec_weight'] = .5
    return config
class ResultRAG(TypedDict):
    retrieved_docs: List[Document]
    answer: str
    exc_second: float

def create_langchain_doc(content: str, metadata: Dict) -> Document:
    '''
        Quickly create langchain Document
    '''
    doc = Document(page_content=content)
    doc.metadata = metadata
    return doc

class TDTDoc:

    def __init__(self, content: str = "", src: str = "", id: str = "", title: str = "") -> None:
        self.content = content.strip()
        self.source = src.strip()
        self.id = id.strip()
        self.title = title.strip()
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