from src.service.provider import ProviderService
import time
from typing import TypedDict, List
from operator import itemgetter
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.documents import Document
from datasets.dataset_dict import DatasetDict 

class ConfigParentRAG(TypedDict):
    vec_index: str
    txt_index: str
    vec_weight: float = 0.5
    txt_weight: float = 0.5
    total_k: int = 4
    llm: str = 'gemini-1.5-flash'


def get_default_config() -> ConfigParentRAG:
    config: ConfigParentRAG = {}
    config['llm'] = "gemini-1.5-flash"
    config['total_k'] = 4
    config['txt_weight'] = .5
    config['vec_weight'] = .5
    return config


class ResultRAG(TypedDict):
    retrieved_docs: List[Document]
    answer: str
    exc_second: float

TEMPLATE = """Bạn là một người tư vấn viên thân thiện và đầy hiểu biết. Nhiệm vụ của bạn là hỗ trợ người dùng hiểu biết hơn về trường đại học {university}.

Đây là thông tin mà bạn biết:
```
{context}
```
Hãy hỗ trợ thật tốt với yêu cầu sau đến từ người dùng.
Yêu cầu (Question): {question}
Hãy trả lời một cách thật ngắn gọn, xúc tích, cấu trúc câu đầy đủ. Output "None" if you cannot answer
"""

class HugFaceParentRAG:

    def __init__(self, provider: ProviderService, config: ConfigParentRAG, text_corpora: DatasetDict, uni="Tôn Đức Thắng") -> None:
        self.ensemble_retriever = provider.get_hybrid_retriever(
            vec_index=config['vec_index'], 
            txt_index=config['txt_index'], 
            total_k=config['total_k'],
            vec_wgh=config['vec_weight'],
            txt_wgh=config['txt_weight'])
        
        gemini = provider.get_simple_gemini_pro(model=config['llm'])
        self.corpora = text_corpora
        self.retrieved_docs = None
        teml = TEMPLATE.replace("{university}", uni)
        prompt = PromptTemplate.from_template(template=teml)
        self.answer_chain = prompt | gemini
        self.chain = (
            {"context": itemgetter("question") | RunnableLambda(self.ensemble_retriever.invoke), 
             "question": itemgetter("question")
            }
            | RunnableLambda(self.__find_parent_docs)
            | RunnableLambda(self.__refine_answer)
        ) 
        return
    
    def answer(self, question: str) -> ResultRAG:
        start = time.time()
        resp = self.chain.invoke({"question": question})
        end = time.time()
        result: ResultRAG = {}
        result['answer'] = resp
        result['retrieved_docs'] = self.retrieved_docs
        result['exc_second'] = end - start
        # reset docs
        self.retrieved_docs = None
        return result

    def __refine_answer(self, inputs):
        answer_doc = ""
        docs = inputs['parent_docs']
        ques = inputs['question']
        for d in docs:
            answer = self.answer_chain.invoke({"context": d, "question": ques})
            answer_doc += (answer + "\n")
        fin_answer = self.answer_chain.invoke({"context": answer_doc, "question": ques})
        return fin_answer


    def __find_parent_docs(self, inputs):
        # store retrieved docs
        docs: List[Document] = inputs['context']
        self.retrieved_docs = docs
        map_ids = {}
        parent_docs:List[str] = []
        for doc in docs:
            print(doc)
            d_id = doc.metadata['doc_id']
            if d_id in map_ids:
                continue
            map_ids[d_id] = 1
            corp_row = self.corpora.filter(lambda e: e['doc_id'] == d_id)
            if len(corp_row) != 1:
                print("ERROR, get id but 2 returned")
            doc_content = '\n- '.join(corp_row[0]['proposition_list'])
            parent_docs.append(doc_content)
        inputs['parent_docs'] = parent_docs
        return inputs