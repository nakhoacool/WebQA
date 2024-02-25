from src.prepare.types import TDTDoc

class RAGCategories:

    def __init__(self) -> None:
        self.major = RAGConfig(
            embed_model = "sentence-transformers/LaBSE",
            text_index = "text-split-major",
            vector_index = "labse-major",
            db_category = "major")
        
        self.uni = RAGConfig(
            embed_model = "sentence-transformers/LaBSE",
            text_index = "text-split-uni",
            vector_index = "labse-uni",
            db_category="uni"
        )
        return


class RAGConfig:
    text_index: str
    vector_index: str
    db_category: str
    embed_model: str

    def __init__(self, embed_model, text_index, vector_index, db_category) -> None:
        self.embed_model = embed_model
        self.text_index = text_index
        self.vector_index = vector_index
        self.db_category = db_category
        return

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
