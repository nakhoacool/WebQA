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

PROMPT_TEMPLATE_v1 = """Given the user question below, classify it as either being about `Major`, `Uni` or `Other`. Known that:
```
    Major: when the question related to a training program (major) of Ton Duc Thang university.
    Major: khi đối tượng được hỏi liên quan đến một ngành đào tạo nào đó.
    Major: khi câu hỏi liên quan đến ngành đào tạo của trường đại học Tôn Đức Thắng. Ví dụ: tư vấn về ngành học, hỏi về ngành học, trường đào tạo ngành học gì, các ngành học có ...
    Uni: when the question asks something specifically about Ton Duc Thang university. For example: what is the university email, location, rules...
    Uni: khi đối tượng được hỏi cụ thể về trường đại học Tôn Đức Thắng, ví dụ: hỏi về thông tin trường, địa chỉ liên lạc, thành tích, ... 
```
Do not respond with more than one word.

<question>
{question}
</question>

Classification:"""

PROMPT_TEMPLATE = """Given the user question below, classify it as either being about `Major`, `Uni`, `Training` or `Other`. Known that:
```
    Major: when the question related to a training program (major) of Ton Duc Thang university.
    Major: khi đối tượng được hỏi liên quan đến một ngành đào tạo nào đó.
    Major: khi câu hỏi liên quan đến ngành đào tạo của trường đại học Tôn Đức Thắng. Ví dụ: tư vấn về ngành học, hỏi về ngành học, trường đào tạo ngành học gì, các ngành học có ...
    Uni: when the question asks something specifically about Ton Duc Thang university. For example: what is the university email, location, rules...
    Uni: khi đối tượng được hỏi cụ thể về trường đại học Tôn Đức Thắng, ví dụ: hỏi về thông tin trường, địa chỉ liên lạc, thành tích, ... 
    Training: khi đối tượng được hỏi liên quan các chương trình đào tạo của trường đại học Tôn Đức Thắng, ví dụ: hỏi về chương trình 4 + 1, chương trình đào tạo tiêu chuẩn,... 
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
            rag_config=provider.get_categories().major_gemini, 
            update_notification_func=self.__invoke_update_notification
        )
        self.uni_rag = HybridGeminiRAG(
            provider=provider,
            rag_config=provider.get_categories().uni_gemini,
            update_notification_func=self.__invoke_update_notification
        )
        self.training_prop_rag = HybridGeminiRAG(
            provider=provider,
            rag_config=provider.get_categories().training_gemini,
            update_notification_func=self.__invoke_update_notification
        )
        # states
        self.is_document_update = False
        self.current_doc:TDTDoc = None
        # chains
        self.default_chain = self.__build_default()
        self.followup = None
        self.main_chain = self.__build_routing()
        return
    
    def __invoke_update_notification(self):
        self.is_document_update = True
        return

    def __build_routing(self):
        self.router = (
            PromptTemplate.from_template(template=PROMPT_TEMPLATE)
            | self.provider.get_gemini_pro()
            | StrOutputParser()
        )
        branch = RunnableBranch(
            (lambda x: "major" in x['topic'].lower(), self.major_rag.chain),
            (lambda x: "uni" in x['topic'].lower(), self.uni_rag.chain),
            (lambda x: "training" in x['topic'].lower(), self.training_prop_rag.chain),
            self.default_chain
        )
        full_chain = {"topic": self.router, "question": lambda x: x["question"]} | branch
        return full_chain
    
    def __update_followup(self, doc: TDTDoc):
        if self.followup == None:
            self.followup = LocalFollowUpChain(provider=self.provider, document=doc)
            return
        self.followup.set_doc(document=doc, reset_memory=True)
        return

    def __build_default(self):
        def __format_default_answer(resp):
            result = RAGResponse(answer=resp, category="default", document="empty.txt")
            return result

        template  = DEFAULT_TEMPLATE.format(context="There is nothing to provide", question="{question}")
        chain = (
            PromptTemplate.from_template(template=template)
            | self.provider.get_gemini_pro(False)
            | StrOutputParser()
            | RunnableLambda(__format_default_answer)
        )
        return chain
    
    def __is_local_question(self, doc: str, question: str) -> bool:
        data = "\n".join([c[:20]+"..." for c in doc.split("\n")]) 
        prompt = f"""Đây là thông tin mà bạn biết:
        ```
        {data}
        ```
        Câu hỏi '{question}' có thể được trả lời bằng đoạn thông tin trên không? 
        Output true or false."""
        ai = self.provider.get_simple_gemini_pro()
        return True if ai(prompt).lower() == "true" else False

    @traceable(tags=["robot"])
    def answer(self, question:str) -> RAGResponse:
        resp: RAGResponse = None
        if self.followup != None and self.__is_local_question(self.current_doc.content, question):
            resp = self.followup.chain.invoke({"question": question})
        else:
            resp = self.main_chain.invoke({"question": question})
        if self.is_document_update:
            self.current_doc = resp.document
            self.__update_followup(doc=resp.document)
            self.is_document_update = False
        return resp