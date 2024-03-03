from src.prepare.data_load import DocDataLoader
from src.prepare.types import TDTDoc

class DocCategories:

    major = "major"
    def __init__(self) -> None:
        
        pass


class DocStore:

    def __init__(self) -> None:
        doc_loader = DocDataLoader()
        self.database = {}
        self.database['major'] = doc_loader.load_major_docs_full_asmap()
        self.database['uni'] = doc_loader.load_docs_full_asmap(file_name="uni_info.csv")
        self.database['training'] = doc_loader.load_docs_full_asmap(file_name="training_program_info.csv")
        return

    def find_document(self, category:str, id: str) -> TDTDoc:
        return self.database[category][id]