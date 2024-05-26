from src.utils.type_utils import TDTDoc
from src.service.applog import AppLogService
from firebase_admin import firestore
from src.service.config import ConfigurationService
from google.cloud.firestore_v1.base_query import FieldFilter

class FirebaseStore:

    def __init__(self, config: ConfigurationService) -> None:
        config.init_firebase_connection() 
        self.db = firestore.client()
        self.path = "Data/TDT/"
        self.log = AppLogService(name="firebase.log")
        return

    def create_document(self, collection: str, document_id: str, document_data: TDTDoc):
        doc_ref = self.db.collection(self.path+collection).document(document_id=document_id)
        try:
            doc_ref.set(document_data.to_json())
        except Exception:
            self.log.logger.exception("[ERROR] can't create document")
        return

    def read_document(self, collection: str, document_id: str) -> TDTDoc:
        doc_ref = self.db.collection(self.path+collection).document(document_id)
        document = doc_ref.get()
        if document.exists:
            doc = TDTDoc() 
            doc.from_json(document.to_dict())
            return doc
        else:
            self.log.logger.warn("No such document with "+document_id+" at "+collection)
            return None

    def find_document_by_title(self, collection: str, title: str) -> TDTDoc:
        docs = (self.db.collection(self.path+collection).where(filter=FieldFilter("title", "==", title)).stream())
        tmp = {}
        for d in docs:
            tmp = d.to_dict()
            if len(tmp.keys()) > 0:
                tdt = TDTDoc()
                tdt.from_json(tmp)
                return tdt
        return None

    def find_document(self, category: str, id: str) -> TDTDoc:
        return self.read_document(collection=category, document_id=id)
        
    def update_document(self, collection: str, document_id: str, update_document: TDTDoc):
        doc_ref = self.db.collection(self.path+collection).document(document_id)
        try:
            if doc_ref.get().exists:
                doc_ref.update(update_document.to_json())
            else:
                self.create_document(collection=collection, document_data=update_document, document_id=document_id)
        except Exception:
            self.log.logger.exception("Can't update")
        return
    
    def delete_document(self, collection: str, document_id:str):
        doc_ref = self.db.collection(self.path+collection).document(document_id)
        try:
            doc_ref.delete()
        except Exception:
            self.log.logger.exception(f"Can't delete doc with id {document_id} at {collection}")
        return
    
    def delete_all(self, collection: str):
        """
            Be careful!! This method wipes out all data
        """
        doc_refs = self.db.collection(self.path+collection).list_documents()
        for ref in doc_refs:
            ref.delete() 
        return
    