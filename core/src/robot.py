from langchain_core.runnables import RunnableBranch
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.service.provider import ProviderService
from src.rag.hybrid_rag import HybridGeminiRAG
from src.prepare.data_load import DocDataLoader
from src.chain.local_followup import LocalFollowUpChain


TEMPLATE = """Given the user question below, classify it as either being about `Major`, `Local` or `Other`. Known that:
```
    Local: when the question related to "ngành kỹ thuật hóa học" or "ngành kỹ thuật hóa học trường Tôn Đức Thắng. This have the highest priority.
    Major: when the question related to a training program (major) of Ton Duc Thang university.
```
Do not respond with more than one word.

<question>
{question}
</question>

Classification:"""

class RAGRobot:

    def __init__(self, provider: ProviderService) -> None:
        self.provider = provider
        self.major_rag = HybridGeminiRAG(
            provider=provider, 
            rag_config=provider.get_categories().major)
        self.followup = self.__build_followup()
        self.other = self.__build_default()
        self.main_chain = self.__build_routing()
        pass


    def __build_followup(self):
        doc_loader = DocDataLoader()
        docs = doc_loader.load_major_docs_full()
        d1 = docs[15]
        followup = LocalFollowUpChain(provider=self.provider, doc_content=d1.page_content)
        return followup
    
    def __build_routing(self):
        template = TEMPLATE
        self.router = (
            PromptTemplate.from_template(template=template)
            | self.provider.get_gemini_pro()
            | StrOutputParser()
        )

        branch = RunnableBranch(
            (lambda x: "local" in x["topic"].lower(), self.followup.chain),
            (lambda x: "major" in x['topic'].lower(), self.major_rag.chain),
            self.other
        )
        full_chain = {"topic": self.router, "question": lambda x: x["question"]} | branch
        return full_chain
    

    def __build_default(self):
        template = "Tell me a joke about {question}"
        chain = (
            PromptTemplate.from_template(template=template)
            | self.provider.get_gemini_pro(False)
            | StrOutputParser()
        )
        return chain
