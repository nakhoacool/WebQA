class TDTDoc:

    def __init__(self, content: str, src: str, id: int, title: str = "") -> None:
        self.content = content
        self.source = src
        self.id = id
        self.title = title
        return
