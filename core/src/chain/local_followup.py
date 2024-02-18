from langsmith.run_helpers import traceable
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain.memory import ConversationBufferMemory
from operator import itemgetter
from src.service.provider import ProviderService
from src.service.applog import AppLogService

TEMPLATE = """"You are a helpful admission assitant for Ton Duc Thang university.
Answer the question mainly using the following context. Output "None" if you cannot answer:
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
    def __init__(self, provider: ProviderService, doc_content: str) -> None:
        """
            Initialize the chain. (a chain is a RAG but without the retriever)
            @param doc_content the input document
            @param config Configuration
        """
        self.chat_model = provider.get_gemini_pro(convert_system_message=True)
        self.doc = doc_content
        self.logservice = AppLogService(name="followup.log")
        self.memory = ConversationBufferMemory(return_messages=True)
        self.chain = self.__build_chain(reset_memory=False)
        return
    
    def set_doc(self, doc_content: str, reset_memory: bool):
        """
            Rebuild the chain with new input document.
            @reset_memory: reset previous memory if true
        """
        self.doc = doc_content
        self.chain = self.__build_chain(reset_memory=reset_memory)
        pass    

    def __build_chain(self, reset_memory:bool = False):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", TEMPLATE.format(doc = self.doc)),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}")])
        if reset_memory:
            self.memory = ConversationBufferMemory(return_messages=True)
        chain = RunnablePassthrough.aschain = (
            {
                "question": itemgetter("question")
            }
            |RunnablePassthrough.assign(
                history=RunnableLambda(self.memory.load_memory_variables) | itemgetter("history"),
            )
            | self.prompt
            | self.chat_model
        )
        return chain

    def invoke(self, data):
        return data['question']

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
