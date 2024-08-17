from langchain.chains import HypotheticalDocumentEmbedder 
from src.service.provider import ProviderService
from typing import Tuple, List
from langchain_core.documents import Document
from src.custom.es_bm25_retriever import MyElasticSearchBM25Retriever
from langchain.retrievers import EnsembleRetriever
from src.service.applog import AppLogService
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from src.utils.type_utils import ConfigParentRAG, ResultRAG
import time

TEMPLATE = """Bạn là một người tư vấn viên thân thiện và đầy hiểu biết. Nhiệm vụ của bạn là hỗ trợ người dùng hiểu biết hơn về trường đại học {uni}.

Hãy kết hợp kiến thức của bạn và đọc thật kỹ các dữ liệu dưới đây để trả lời câu hỏi:
```
{context}
```
Câu hỏi: {question}?

Hãy trả lời một cách thật hữu ích, ngắn gọn, xúc tích, cấu trúc câu đầy đủ. Output "None" if you cannot answer
"""

SEPERATOR = "# Dữ liệu"

class HydeRAG:

    def __init__(self, provider: ProviderService, index: str, k: int = 4) -> None:
        self.es = provider.get_elasticsearch_store(index=index)
        self.gemini = provider.get_simple_gemini_pro()
        self.base_emdeddings = provider.get_gemini_embeddings()
        self.embeddings = HypotheticalDocumentEmbedder.from_llm(self.gemini, self.base_emdeddings, "web_search")
        self.k = k
        self.errors = []
        self.log = AppLogService(f"hyde-rag-{index}.log")
        return
    
    def search(self, question:str) -> List[Tuple[Document, float]]:
        hyde_doc = None
        try:
            hyde_doc = self.embeddings.invoke(question)
        except Exception:
            self.log.logger.exception(msg=f"[can't answer RAG] {question}")
            return None
        if(hyde_doc == None or len(hyde_doc['text']) <= 0):
            self.errors.append(question)
            return None
        docs = self.es.similarity_search_with_relevance_scores(query=hyde_doc['text'], k=self.k)
        return docs

class RAG:

    def __init__(self, provider: ProviderService, config: ConfigParentRAG, uni: str) -> None:
        self.rag_config = config
        self.uni = uni
        self.gemini = provider.get_simple_gemini_pro(model=config["llm"])
        self.base_emdeddings = provider.get_gemini_embeddings()
        es = provider.get_elasticsearch_store(index=config['vec_index'], embed_type='gemini')
        K = config['total_k']
        self.ensemble_retriever = es.as_retriever(search_kwargs={"k": K, "fetch_k": 10})
        self.retrieve_docs = None
        self.chain = self.__build_chain()
        self.log = AppLogService(f"rag-{config['vec_index']}.log")
        return
    
    def answer(self, question: str) -> ResultRAG:
        result: ResultRAG = {}
        ans = ''
        try:
            start = time.time()
            ans = self.chain.invoke(question)
            end = time.time()
            result['answer'] = ans
            result['exc_second'] = end - start
            result['retrieved_docs'] = self.retrieve_docs
            # reset docs
            self.retrieved_docs = None
        except Exception:
            print(f"ERROR: {question}")
            self.log.logger.exception(msg=f"[NO ANSWER] {question}")
            return result
        return result
    
    def __build_chain(self):
        """
            Note! private method

            Initialize the RAG chain.
        """
        prompt = PromptTemplate.from_template(template=TEMPLATE.replace("{uni}", self.uni))
        rag = (
            {"context": self.ensemble_retriever | self.__store_docs | self.__format_doc,
                 "question": RunnablePassthrough()} | prompt | self.gemini)
        return rag

    def __format_doc(self, docs: List[Document]):
        """
            Note! private method

            Prepare list of docs into a single string
        """
        doc_str = ""
        for idx, d in enumerate(docs):
            doc_str = f"{doc_str}\n {SEPERATOR} {idx+1}:\n{d.page_content}\n"
        return doc_str

    def __store_docs(self, docs: List[Document]):
        """
            Note! private method

            Store the retrieved documents to a list.
        """
        self.retrieve_docs = docs
        return docs
    

class HydeHybridSearchRAG:

    def __init__(self, provider: ProviderService, config: ConfigParentRAG, uni: str) -> None:
        self.rag_config = config
        self.gemini = provider.get_simple_gemini_pro(model=config["llm"])
        self.base_emdeddings = provider.get_gemini_embeddings()
        self.uni = uni 
        self.ensemble_retriever = provider.get_hybrid_retriever(
            vec_index=config['vec_index'], 
            txt_index=config['txt_index'], 
            total_k=config['total_k'],
            vec_wgh=config['vec_weight'],
            txt_wgh=config['txt_weight'])
        self.embeddings = HypotheticalDocumentEmbedder.from_llm(self.gemini, self.base_emdeddings, "web_search")
        self.retrieve_docs = None
        self.chain = self.__build_chain()
        
        self.log = AppLogService(f"hyde-hybrid-rag-{config['vec_index']}.log")
        return
    
    def search(self, question:str) -> List[Tuple[Document, float]]:
        hyde_doc = None
        try:
            hyde_doc = self.embeddings.invoke(question)
        except Exception:
            self.log.logger.exception(msg=f"[can't answer RAG] {question}")
            return None
        if(hyde_doc == None or len(hyde_doc['text']) <= 0):
            return None
        docs = self.ensemble_retriever.invoke(hyde_doc["text"])
        return docs
    
    def answer(self, question: str) -> ResultRAG:
        result: ResultRAG = {}
        ans = ''
        try:
            start = time.time()
            hyde_doc = self.embeddings.invoke(question)
            hyde_ques = hyde_doc['text']
            print(hyde_doc)
            if hyde_ques is None or len(hyde_ques) <= 0:
                return ""
            ans = self.chain.invoke(question)
            end = time.time()
            result['answer'] = ans
            result['exc_second'] = end - start
            result['retrieved_docs'] = self.retrieve_docs
            # reset docs
            self.retrieved_docs = None
        except Exception:
            print(f"ERROR: {question}")
            self.log.logger.exception(msg=f"[NO ANSWER] {question}")
            return result
        return result
    
    def __build_chain(self):
        """
            Note! private method

            Initialize the RAG chain.
        """
        prompt = PromptTemplate.from_template(template=TEMPLATE.replace("{uni}", self.uni))
        rag = (
            {"context": self.ensemble_retriever | self.__store_docs | self.__format_doc,
                 "question": RunnablePassthrough()} | prompt | self.gemini)
        return rag

    def __format_doc(self, docs: List[Document]):
        """
            Note! private method

            Prepare list of docs into a single string
        """
        doc_str = ""
        for idx, d in enumerate(docs):
            doc_str = f"{doc_str}\n {SEPERATOR} {idx+1}:\n{d.page_content}\n"
        return doc_str

    def __store_docs(self, docs: List[Document]):
        """
            Note! private method

            Store the retrieved documents to a list.
        """
        self.retrieve_docs = docs
        return docs