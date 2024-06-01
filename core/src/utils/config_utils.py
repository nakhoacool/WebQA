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
        self.folder_name = f"{db_category}"
        return

def get_gemini_hyde_config() -> RAGConfig:
    '''
        Gemini
        Hyde
        Hybrid search
    '''
    config = RAGConfig(
        embed_model="gemini",
        text_index="text-hyde-hybrid",
        vector_index='vector-hyde-hybrid',
        db_category='hyde-hybrid',
        size=1500,
        overlap=50
    )
    return config