from src.service.provider import ProviderService
import time
from typing import TypedDict, List
from operator import itemgetter
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_core.documents import Document
from datasets.dataset_dict import DatasetDict 
from src.service.applog import AppLogService

from src.utils.type_utils import ConfigParentRAG, ResultRAG

OLD_TEMPLATE1 = """Bạn là một người tư vấn viên thân thiện và đầy hiểu biết. Nhiệm vụ của bạn là hỗ trợ người dùng hiểu biết hơn về trường đại học {university}.

Đây là thông tin mà bạn biết:
```
{context}
```
Hãy hỗ trợ thật tốt với yêu cầu sau đến từ người dùng.
Yêu cầu (Question): {question}
Hãy trả lời một cách thật ngắn gọn, xúc tích, cấu trúc câu đầy đủ. Output "None" if you cannot answer
"""

TEMPLATE = """Bạn là một người tư vấn viên thân thiện và đầy hiểu biết. Nhiệm vụ của bạn là hỗ trợ người dùng hiểu biết hơn về trường đại học {university}.

Hãy kết hợp kiến thức của bạn và đọc thật kỹ các dữ liệu dưới đây để trả lời câu hỏi:
```
{context}
```
Câu hỏi: {question}?

Hãy trả lời một cách thật hữu ích, cấu trúc câu đầy đủ nếu bạn có thể trả lời. Output only "None" if you cannot answer.
"""

REFINE_TEMPLATE = """Bạn là một người tư vấn viên thân thiện và đầy hiểu biết. Nhiệm vụ của bạn là hỗ trợ người dùng hiểu biết hơn về trường đại học {university}.

Hãy kết hợp kiến thức của bạn và dữ liệu dưới đây để trả lời câu hỏi:
```
{context}
```
Câu hỏi: {question}?

Hãy trả lời một cách thật hữu ích và đầy đủ nội dung, và chi tiết, hợp lý.
Hãy đưa ra lời khuyên hữu ích từ kiến thức của bạn nếu như không thể trả lời câu hỏi.
"""

def is_can_answer(answer:str):
    text = answer.lower()
    return "none" not in text.split(" ") and "không đề cập" not in text

class HugFaceParentRAG:

    def __init__(self, provider: ProviderService, config: ConfigParentRAG, text_corpora: DatasetDict, uni: str) -> None:
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
        self.refine_answer_chain = PromptTemplate.from_template(REFINE_TEMPLATE.replace("{university}", uni)) | gemini
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
            if len(docs) == 1:
                return answer
            if is_can_answer(answer=answer):
                answer_doc += (answer + "\n")
        fin_answer = self.refine_answer_chain.invoke({"context": answer_doc, "question": ques})
        return fin_answer


    def __find_parent_docs(self, inputs):
        # store retrieved docs
        docs: List[Document] = inputs['context']
        self.retrieved_docs = docs
        map_ids = {}
        parent_docs:List[str] = []
        if self.corpora is None:
            doc_content = "\n".join([d.page_content for d in docs])
            inputs['parent_docs'] = [doc_content]
            return inputs
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

class HugFaceParentParallelRAG:

    def __init__(self, provider: ProviderService, config: ConfigParentRAG, text_corpora: DatasetDict, uni="Tôn Đức Thắng") -> None:
        self.ensemble_retriever = provider.get_hybrid_retriever(
            vec_index=config['vec_index'], 
            txt_index=config['txt_index'], 
            total_k=config['total_k'],
            vec_wgh=config['vec_weight'],
            txt_wgh=config['txt_weight'])
        
        self.log = AppLogService(f"{config['vec_index']}.log")
        self.gemini = provider.get_simple_gemini_pro(model=config['llm'])
        self.corpora = text_corpora
        self.template = TEMPLATE.replace("{university}", uni)
        self.retrieved_docs = None
        self.batch = 2
        self.refine_answer_chain = PromptTemplate.from_template(REFINE_TEMPLATE.replace("{university}", uni)) | self.gemini
        self.chain = (
            {"context": itemgetter("question") | RunnableLambda(self.ensemble_retriever.invoke), 
             "question": itemgetter("question")
            }
            | RunnableLambda(self.__find_parent_docs)
            | RunnableLambda(self.__parallel_answer)
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

    def __parallel_answer(self, inputs):
        answers = []
        docs = inputs['parent_docs']
        ques = inputs['question']
        chains = [{}]
        batch = 0
        print("2. start answer")
        # split documents to batches of chains
        for idx, d in enumerate(docs):
            prompt = PromptTemplate.from_template(
                template=self.template.replace("{context}",d))
            answer_chain = prompt | self.gemini
            chains[batch][str(idx)] = answer_chain
            if idx % self.batch == 0 and idx > 0:
                batch += 1
                chains.append({})
        # run each batch one by one
        for chain_batch in chains:
            parallel_chain = RunnableParallel(**chain_batch)
            try:
                ans_list = parallel_chain.invoke({"question": ques})
            except Exception:
                ans_list = {'1': ''}
                self.log.logger.exception(Exception)
            answers.extend(list(ans_list.values()))
        return {"answers": answers, "question": ques}

    def __refine_answer(self, inputs):
        context = "\n- ".join([a for a in inputs['answers'] if is_can_answer(answer=a)])
        answer = self.refine_answer_chain.invoke({"context": context, "question": inputs['question']})
        return answer

    def __find_parent_docs(self, inputs):
        # store retrieved docs
        docs: List[Document] = inputs['context']
        self.retrieved_docs = docs
        map_ids = {}
        parent_docs:List[str] = []
        for doc in docs:
            d_id = doc.metadata['doc_id']
            if d_id in map_ids:
                continue
            map_ids[d_id] = 1
            corp_row = self.corpora.filter(lambda e: e['doc_id'] == d_id)
            if len(corp_row) != 1:
                print("ERROR, get id but 2 returned")
            doc_content = corp_row[0]['content']
            parent_docs.append(doc_content)
        inputs['parent_docs'] = parent_docs
        print('1. Find parent')
        return {'question': inputs['question'], "parent_docs": parent_docs}