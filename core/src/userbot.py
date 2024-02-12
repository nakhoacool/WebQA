from typing import List
from src.rag.types import TDTDoc
from src.masterbot import MasterBot
from src.chain.followup import LocalFollowUpChain
from src.config import Configuration
from src.rag.types import RAGResponse
from src.prepare.types import TDTDoc

class UserBot:
    
    def __init__(self, user_id: str, masterRef: MasterBot) -> None:
        self.id = user_id
        self.resfresh_rag = True
        self.lastest_doc:TDTDoc = None
        self.local_chain = None
        self.master_bot = masterRef
        self.conf = Configuration() 
        self.err_msg = "Sorry! I can't find anything related to your question."
        return

    def ask(self, question: str) -> RAGResponse:
        if self.resfresh_rag:
            return self.ask_master_bot(question=question)
        ans = self.local_chain.answer(question=question)
        if ans.lower() == "none":
            del self.local_chain
            self.resfresh_rag = True
        resp = RAGResponse(answer=ans, category="local", document=self.lastest_doc)
        return resp

    def ask_master_bot(self, question: str) -> RAGResponse:
        # ask master bot
        resp = self.master_bot.ask_rags(question=question)
        # init local chain
        self.local_chain = LocalFollowUpChain(config=self.conf, doc_content=resp.document.content)
        self.resfresh_rag = False
        self.lastest_doc = resp.document
        return resp