from langsmith.run_helpers import traceable
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain.memory import ConversationBufferMemory
from operator import itemgetter
from src.service.provider import ProviderService
from src.service.applog import AppLogService
from src.rag.types import RAGResponse
from src.utils.type_utils import TDTDoc

TEMPLATE = """"You are a helpful and friendly assitant for Ton Duc Thang university.
Answer the question using the following context and your knowledge to best support the user. Output "None" if you cannot answer:
```
{doc}
```
"""

TEMPLATE = """Bạn là một người tư vấn viên thân thiện và đầy hiểu biết. Nhiệm vụ của bạn là hỗ trợ người dùng hiểu biết hơn về trường đại học Tôn Đức Thắng.

Đây là thông tin mà bạn biết:
```
{doc}
```
Hãy hỗ trợ thật tốt với yêu cầu sau đến từ người dùng. Output "None" if you cannot answer.
"""

class LocalFollowUpChain:
    """
        This chain is design to answer follow up question, provided that you give an input document.
        It acts as a document
        It uses:
        - Gemini as chat model
        - ConversationBufferMemory as memory
    """
    def __init__(self, provider: ProviderService, document: TDTDoc) -> None:
        """
            Initialize the chain. (a chain is a RAG but without the retriever)
            @param document the input document
            @param provider the service provider
        """
        self.webloader = provider.webloader
        self.chat_model = provider.get_gemini_pro(convert_system_message=True)
        self.logservice = AppLogService(name="local_followup.log")
        self.memory = ConversationBufferMemory(return_messages=True)
        self.set_doc(document=document, reset_memory=False)
        self.chain = self.__build_chain(doc=document,reset_memory=False)
        return
    
    def set_doc(self, document: TDTDoc, reset_memory: bool):
        """
            Rebuild the chain with new input document.
            @reset_memory: reset previous memory if true
        """
        if document.source.lower() != "none":
            load_doc = self.webloader.load_page(link=document.source)
            if load_doc != None:
                document.set_content(load_doc)
        self.current_document = document
        self.chain = self.__build_chain(doc=document,reset_memory=reset_memory)
        return

    def __build_chain(self, doc:TDTDoc, reset_memory:bool = False):
        doc_content = doc.content
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", TEMPLATE.format(doc = doc_content)),
            MessagesPlaceholder(variable_name="history"),
            ("human", "Yêu cầu: {question}")])
        if reset_memory:
            self.memory = ConversationBufferMemory(return_messages=True)

        chain = RunnablePassthrough.aschain = (
            {
                "question": itemgetter("question")
            }
            | RunnableLambda(self.__save_input_format_question)
            |RunnablePassthrough.assign(
                history=RunnableLambda(self.memory.load_memory_variables) | itemgetter("history"),
            )
            | self.prompt
            | self.chat_model
            | RunnableLambda(self.__save_format_answer)
        )
        return chain

    def __save_input_format_question(self, input):
        # save input for history
        question = input["question"]
        # format question
        self.inputs = {"question": question}
        template = f"Hãy tham khảo từ văn bản được cho để trả lời câu hỏi '{question}'. Output 'None' if you cannot answer or there are no information metioned."
        input['question'] = template
        return input

    def __save_format_answer(self, resp):
        """
            This method formats the response to RAGResponse type
        """
        self.memory.save_context(inputs=self.inputs, outputs={"output": resp.content})
        result = RAGResponse(answer=resp.content, category="local", document=self.current_document)
        return result

    @traceable(tags=["followup"])
    def answer(self, question: str) -> RAGResponse:
        try:
            response = self.chain.invoke({"question": question})
        except Exception as err:
            self.logservice.logger.exception("InvokeChainError")
            return "[Followup] Sorry! something went wrong"
        return response
