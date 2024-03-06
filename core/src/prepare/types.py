from typing import Dict

class TDTDoc:

    def __init__(self, content: str = "", src: str = "", id: int = 0, title: str = "") -> None:
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
        
