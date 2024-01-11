import streamlit as st
import sys
import os
PATH = os.path.dirname(__file__)+"/../"
sys.path.append(PATH)

from src.config import Configuration
from src.rag.doc_split_rag import DocSplitRag
from src.rag.hybrid_rag import HybridRag

MODEL = "sentence-transformers/LaBSE"

def main(config: Configuration, rag):
    st.title("Semantic search for majors")
    st.header("Find your major")

    api_key = config.load_hg_token()

    if api_key == None or len(api_key) == 0:
        return

    if api_key:
        st.write("Enter your query and we will find the most similar majors to yours")
        query = st.text_input("Enter your query")
        if query:
            st.write("Your most similar majors are:")
            # st.write(rag.get_retriever().similarity_search_with_score(query))
            st.write(rag.get_retriever().get_relevant_documents(query))

if __name__ == "__main__":
    config = Configuration()
    # rag = DocSplitRag(data_path=os.path.join(PATH, "./data/"))
    rag = HybridRag(data_path=os.path.join(PATH, "./data/"))
    print("Building")
    # rag.build(hug_token=config.load_hg_token())
    rag._build()
    print("Done build rag")
    main(config, rag=rag)
