from src.prepare.types import TDTDoc

class RAGCategories:

    def __init__(self) -> None:
        # Major
        self.tdt_gemini = RAGConfig(
            embed_model="gemini",
            text_index="tdt-text-split-gemini",
            vector_index="tdt-vec-gemini",
            db_category="tdt"
        )
        self.major = RAGConfig(
            embed_model = "sentence-transformers/LaBSE",
            text_index = "text-split-major",
            vector_index = "labse-major",
            db_category = "major")
        
        self.major_gemini = RAGConfig(
            embed_model="gemini",
            text_index="major-text-split-gemini",
            vector_index="major-vec-gemini",
            db_category="major"
        )
        
        self.major_openai = RAGConfig(
            embed_model="openai",
            text_index="major-text-split-openai",
            vector_index="major-vec-openai",
            db_category="major",
            size=1100,
            overlap=60
        )

        # University
        self.uni = RAGConfig(
            embed_model = "sentence-transformers/LaBSE",
            text_index = "text-split-uni",
            vector_index = "labse-uni",
            db_category="uni"
        )
        self.uni_labse = self.uni
        
        self.uni_openai =  RAGConfig(
            embed_model="openai",
            text_index="uni-text-split-openai",
            vector_index="uni-vec-openai",
            db_category="uni",
            size=460,
            overlap=20
        )

        self.uni_gemini =  RAGConfig(
            embed_model="gemini",
            text_index="uni-text-split-gemini",
            vector_index="uni-vec-gemini",
            db_category="uni"
        )

        # Training program
        self.training_hg = RAGConfig(
            embed_model = "sentence-transformers/LaBSE",
            text_index = "training-text-split-hg",
            vector_index = "training-vec-hg",
            db_category="training",
            size=800,
            overlap=40
        )

        self.training_gemini = RAGConfig(
            embed_model="gemini",
            text_index="training-text-split-gemini",
            vector_index="training-vec-gemini",
            db_category="training",
            size=800,
            overlap=40
        )

        self.training_openai = RAGConfig(
            embed_model="openai",
            text_index="training-text-split-openai",
            vector_index="training-vec-openai",
            db_category='training',
            size=800,
            overlap=40
        )
        
        self.sample = RAGConfig(
            embed_model = "gemini",
            text_index = "text-split-sample",
            vector_index = "gemini-sample",
            db_category="sample" 
        )
        return


class RAGConfig:
    text_index: str
    vector_index: str
    db_category: str
    embed_model: str
    size: int
    overlap: int
    folder_name: str

    def __init__(self, embed_model, text_index, vector_index, db_category, size=460, overlap=20) -> None:
        self.embed_model = embed_model
        self.text_index = text_index
        self.vector_index = vector_index
        self.db_category = db_category
        self.size = size
        self.overlap = overlap
        if db_category == "training":
            self.folder_name = "training_program"
        else:
            self.folder_name = f"{db_category}"
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
