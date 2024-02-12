from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langsmith.run_helpers import traceable
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain.memory import ConversationBufferMemory
from operator import itemgetter
from src.config import Configuration

class LocalFollowUpChain:
    """
        This chain is design to answer follow up question, provided that you give an input document.
        It acts as a document
        It uses:
        - Gemini as chat model
        - ConversationBufferMemory as memory
    """
    def __init__(self, config: Configuration, doc_content: str) -> None:
        """
            Initialize the chain. (a chain is a RAG but without the retriever)
            @param doc_content the input document
            @param config Configuration
        """
        self.chat_model = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0,
            convert_system_message_to_human=True,
            google_api_key=config.load_gemini_token()
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", f'You are a helpful admission assitant for Ton Duc Thang university.\nGive you the following context to answer my questions. Output "None" if you cannot answer:\n```\n{doc_content}\n```\n'),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}")])

        self.memory = ConversationBufferMemory(return_messages=True)
        self.chain = RunnablePassthrough.aschain = (
            {
                "question": itemgetter("question")
            }
            |RunnablePassthrough.assign(
                history=RunnableLambda(self.memory.load_memory_variables) | itemgetter("history"),
            )
            | self.prompt
            | self.chat_model
        )
        return

    @traceable(tags=["followup"])
    def answer(self, question: str) -> str:
        inputs = {"question": question}
        response = self.chain.invoke(inputs)
        self.memory.save_context(inputs=inputs, outputs={"output": response.content})
        return response.content