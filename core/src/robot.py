from langchain_core.runnables import RunnableLambda
from langchain_core.runnables import RunnableBranch
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.service.provider import ProviderService
from src.rag.hybrid_rag import HybridGeminiRAG
from src.prepare.data_load import DocDataLoader
from src.chain.local_followup import LocalFollowUpChain
from langsmith.run_helpers import traceable
from src.rag.types import RAGResponse
from src.prepare.types import TDTDoc

TEMPLATE = """Given the user question below, classify it as either being about `Major`, `Local` or `Other`. Known that:
```
    Major: when the question related to a training program (major) of Ton Duc Thang university.
    Major: khi câu hỏi liên quan đến ngành đào tạo của trường đại học Tôn Đức Thắng. Ví dụ: hỏi về ngành học, trường đào tạo ngành học gì, các ngành học có ...
    Local: when the question specifically related to "{local}" or "{local} trường Tôn Đức Thắng".
```
Do not respond with more than one word.

<question>
{question}
</question>

Classification:"""

DEFAULT_TEMPLATE = """Given the context below
<context>
{context}
</context>

Please answer my question: {question}"""

PROMPT_TEMPLATE = """Given the user question below, classify it as either being about `Major` or `Other`. Known that:
```
    Major: when the question related to a training program (major) of Ton Duc Thang university.
    Major: khi đối tượng được hỏi liên quan đến một ngành đào tạo nào đó.
    Major: khi câu hỏi liên quan đến ngành đào tạo của trường đại học Tôn Đức Thắng. Ví dụ: tư vấn về ngành học, hỏi về ngành học, trường đào tạo ngành học gì, các ngành học có ...
```
Do not respond with more than one word.

<question>
{question}
</question>

Classification:"""

class RAGRobot:

    def __init__(self, provider: ProviderService) -> None:
        """
            Initialize Master Robot. Its purpose is to choose which RAG for which question
            @provider the service provider
        """
        self.provider = provider
        self.major_rag = HybridGeminiRAG(
            provider=provider, 
            rag_config=provider.get_categories().major, 
            update_notification_func=self.__invoke_update_notification)
        # states
        self.is_document_update = False
        self.previous_doc:TDTDoc = None
        # chains
        self.default_chain = self.__build_default()
        self.followup = self.__build_followup()
        self.main_chain = self.__build_routing()
        return
    
    def __invoke_update_notification(self, input):
        self.is_document_update = True
        return input

    def __build_followup(self):
        doc_loader = DocDataLoader()
        docs = doc_loader.load_major_docs_full_asmap()
        d1 = docs[15]
        self.previous_doc = d1
        followup = LocalFollowUpChain(
            provider=self.provider, 
            document=d1)
        return followup
    
    def __build_routing(self):
        self.router = (
            PromptTemplate.from_template(template=PROMPT_TEMPLATE)
            | self.provider.get_gemini_pro()
            | StrOutputParser()
        )

        branch = RunnableBranch(
            (lambda x: "major" in x['topic'].lower(), self.major_rag.chain),
            self.default_chain
        )
        full_chain = {"topic": self.router, "question": lambda x: x["question"]} | branch
        return full_chain
    
    def __update_followup(self, doc: TDTDoc):
        if not self.is_document_update:
            return
        self.followup.set_doc(document=doc, reset_memory=True)
        self.main_chain = self.__build_routing()
        return

    def __build_default(self):
        docs = DocDataLoader().load_major_docs_full_asmap()
        d1 = docs[1]

        def __format_default_answer(resp):
            result = RAGResponse(answer=resp, category="default", document=d1)
            return result

        template  = DEFAULT_TEMPLATE.format(context=d1.content, question="{question}")
        chain = (
            PromptTemplate.from_template(template=template)
            | self.provider.get_gemini_pro(False)
            | StrOutputParser()
            | RunnableLambda(__format_default_answer)
        )
        return chain
    
    @traceable(tags=["robot"])
    def answer(self, question:str) -> RAGResponse:
        resp:RAGResponse = self.followup.chain.invoke({"question": question})
        if "none" != resp.answer.lower():
            return resp
        resp:RAGResponse = self.main_chain.invoke({"question": question})
        if self.is_document_update:
            self.previous_doc = resp.document
            self.__update_followup(doc=resp.document)
            self.is_document_update = False
        return resp