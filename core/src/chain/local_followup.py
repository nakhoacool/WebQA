from langsmith.run_helpers import traceable
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain.memory import ConversationBufferMemory
from operator import itemgetter
from src.service.provider import ProviderService
from src.service.applog import AppLogService
from src.rag.types import RAGResponse
from src.prepare.types import TDTDoc

TEMPLATE = """"You are a helpful and friendly assitant for Ton Duc Thang university.
Answer the question using the following context and your knowledge to best support the user. Output "None" if you cannot answer:
```
{doc}
```
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
        self.doc:TDTDoc = document
        self.logservice = AppLogService(name="local_followup.log")
        self.memory = ConversationBufferMemory(return_messages=True)
        self.chain = self.__build_chain(reset_memory=False)
        return
    
    def set_doc(self, document: TDTDoc, reset_memory: bool):
        """
            Rebuild the chain with new input document.
            @reset_memory: reset previous memory if true
        """
        if document.source.lower() != "none":
            doc = self.webloader.load_page(link=document.source)
            if not doc == None:
                document.content = doc
        self.doc = document
        self.chain = self.__build_chain(reset_memory=reset_memory)
        pass

    def __build_chain(self, reset_memory:bool = False):
        doc_content = self.doc.content
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", TEMPLATE.format(doc = doc_content)),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}")])
        if reset_memory:
            self.memory = ConversationBufferMemory(return_messages=True)
        chain = RunnablePassthrough.aschain = (
            {
                "question": itemgetter("question")
            }
            | RunnableLambda(self.__save_inputs)
            |RunnablePassthrough.assign(
                history=RunnableLambda(self.memory.load_memory_variables) | itemgetter("history"),
            )
            | self.prompt
            | self.chat_model
            | RunnableLambda(self.__format_answer)
        )
        return chain

    def __save_inputs(self, input):
        self.inputs = {"question": input['question']}
        return input

    def __format_answer(self, resp):
        """
            This method formats the response to RAGResponse type
        """
        self.memory.save_context(inputs=self.inputs, outputs={"output": resp.content})
        result = RAGResponse(answer=resp.content, category="local", document=self.doc)
        return result

    @traceable(tags=["followup"])
    def answer(self, question: str) -> str:
        template = f"Only use the given context to answer '{question}'. Output 'None' if you cannot answer."
        inputs = {"question": template}
        try:
            response = self.chain.invoke(inputs)
            self.memory.save_context(inputs=inputs, outputs={"output": response.content})
        except Exception as err:
            self.logservice.logger.exception("InvokeChainError")
            return "[Followup] Sorry! something went wrong"
        return response.content
