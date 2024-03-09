from src.prepare.types import FirebaseTDTDoc
from src.service.applog import AppLogService
import os
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict
from uuid import uuid4

class FirebaseStore:

    def __init__(self) -> None:
        env_path = os.path.dirname(__file__)
        path = f"{env_path}/../../.keys"
        cred = credentials.Certificate(path+'/firebaseAccountKey.json')
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self.log = AppLogService(name="firebase.log")
        return

    def create_document(self, collection: str, document_id: str, document_data: FirebaseTDTDoc):
        doc_ref = self.db.collection(collection).document(document_id=document_id)
        try:
            doc_ref.set(document_data.to_json())
        except Exception:
            self.log.logger.exception("[ERROR] can't create document")
        return

    def read_document(self, collection: str, document_id: str) -> FirebaseTDTDoc:
        doc_ref = self.db.collection(collection).document(document_id)
        document = doc_ref.get()
        if document.exists:
            doc = FirebaseTDTDoc(doc = None) 
            doc.from_json(document.to_dict())
            return doc
        else:
            self.log.logger.warn("No such document with "+document_id+" at "+collection)
            return None
        
    def update_document(self, collection: str, document_id: str, update_data: Dict):
        doc_ref = self.db.collection(collection).document(document_id)
        try:
            doc_ref.update(update_data)
        except Exception:
            self.log.logger.exception("Can't update")
        return
    
    def delete_document(self, collection: str, document_id:str):
        doc_ref = self.db.collection(collection).document(document_id)
        try:
            doc_ref.delete()
        except Exception:
            self.log.logger.exception(f"Can't delete doc with id {document_id} at {collection}")
        return
    