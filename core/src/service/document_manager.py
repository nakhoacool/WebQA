from src.prepare.data_load import DocDataLoader
from src.prepare.types import TDTDoc
from src.service.applog import AppLogService
import os
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict

class FirebaseDocStore:

    def __init__(self) -> None:
        env_path = os.path.dirname(__file__)
        path = f"{env_path}/../../.keys"
        cred = credentials.Certificate(path+'/firebaseAccountKey.json')
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self.log = AppLogService(name="firebase.log")
        return

    def create_document(self, collection, document_data: TDTDoc):
        doc_ref = self.db.collection(collection).document()
        try:
            doc_ref.set(document_data.to_json())
        except Exception:
            self.log.logger.exception("[ERROR] can't create document")
        return

    def read_document(self, collection: str, document_id: int):
        doc_ref = self.db.collection(collection).document(document_id)
        document = doc_ref.get()
        if document.exists:
            doc = TDTDoc()
            doc.from_json(document)
            return doc
        else:
            self.log.logger.warn("No such document with "+document_id+" at "+collection)
            return None
        
    def update_document(self, collection: str, document_id: int, update_data: Dict):
        doc_ref = self.db.collection(collection).document(document_id)
        try:
            doc_ref.update(update_data)
        except Exception:
            self.log.logger.exception("Can't update")
        return
    
    # Delete a document from Firestore
    def delete_document(self, collection: str, document_id:int):
        doc_ref = self.db.collection(collection).document(document_id)
        try:
            doc_ref.delete()
        except Exception:
            self.log.logger.exception(f"Can't delete doc with id {document_id} at {collection}")
        return