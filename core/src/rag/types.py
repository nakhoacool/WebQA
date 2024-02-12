from src.prepare.types import TDTDoc

class RAGCategories:
    major = "major"

    def __init__(self) -> None:
        pass

class RAGResponse:

    def __init__(self, answer: str, category: str, document: TDTDoc) -> None:
        self.answer = answer
        self.category = category
        self.document = document
        if answer.lower() == "none":
            self.status = 404
        else:
            self.status = 200
        return
    
    def is_sucess(self):
        return True if self.status == 200 else False
    
    def is_notfound(self):
        return True if self.status == 404 else False
