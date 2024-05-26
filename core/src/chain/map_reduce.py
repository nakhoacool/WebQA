from langchain.chains import (
    StuffDocumentsChain,
    ReduceDocumentsChain,
    LLMChain,
    MapReduceDocumentsChain,
)
from langchain_core.prompts import PromptTemplate
from src.service.provider import ProviderService

SUMMARIZE_PROMPT = "Summarize this content: {context}"

REDUCE_PROMPT = "Combine these summaries: {context}"

COLLASPE_PROMPT = "Collapse this content: {context}"

def create_map_reduce_chain(provider: ProviderService) -> MapReduceDocumentsChain:
    document_prompt = PromptTemplate( input_variables=["page_content"],
        template="{page_content}"
    )
    document_variable_name = "context"
    prompt = PromptTemplate.from_template(SUMMARIZE_PROMPT)

    gemini = provider.get_simple_gemini_pro()
    sum_chain = LLMChain(prompt=prompt, llm=gemini)
    
    # Reduce
    reduce_prompt = PromptTemplate.from_template(REDUCE_PROMPT)
    reduce_chain = LLMChain(prompt=reduce_prompt, llm=gemini)
    
    # Combine
    combine_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_chain,
        document_prompt=document_prompt,
        document_variable_name=document_variable_name
    )

    reduce_documents_chain = ReduceDocumentsChain(
        combine_documents_chain=combine_documents_chain,
    )

    chain = MapReduceDocumentsChain(
        llm_chain=sum_chain,
        reduce_documents_chain=reduce_documents_chain,
    )

    return chain