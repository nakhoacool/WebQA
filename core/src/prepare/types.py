class TDTDoc:

    def __init__(self, content: str, src: str, id: int, title: str = "") -> None:
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
        
