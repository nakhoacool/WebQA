from __future__ import annotations

from typing import Any, Dict, Iterable, List

from langchain_core.documents import Document
import uuid
from elasticsearch import Elasticsearch

from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun

class MyElasticSearchBM25Retriever(BaseRetriever):
    """`Elasticsearch` retriever that uses `BM25` extended version.
        @param client ElasticSearchClient
        @param index_name an index
    """

    k: int = 4
    """k size search"""

    client: Elasticsearch
    """Elasticsearch client."""

    index_name: str
    """Name of the index to use in Elasticsearch."""

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Dict,
        refresh_indices: bool = True,
    ) -> List[str]:
        """Run more texts through the embeddings and add to the retriever.

        Args:
            texts: Iterable of strings to add to the retriever.
            refresh_indices: bool to refresh ElasticSearch indices

        Returns:
            List of ids from adding the texts into the retriever.
        """
        try:
            from elasticsearch.helpers import bulk
        except ImportError:
            raise ValueError(
                "Could not import elasticsearch python package. "
                "Please install it with `pip install elasticsearch`."
            )
        requests = []
        ids = []
        for i, text in enumerate(texts):
            metadata = metadatas[i] if metadatas else {}
            _id = str(uuid.uuid4())
            request = {
                "_op_type": "index",
                "_index": self.index_name,
                "content": text,
                "metadata": metadata,
                "_id": _id,
            }
            ids.append(_id)
            requests.append(request)
        bulk(self.client, requests)

        if refresh_indices:
            self.client.indices.refresh(index=self.index_name)
        return ids
    
    def add_documents(self, documents: List[Document], **kwargs: Any) -> List[str]:
        """Run more documents through the embeddings and add to the vectorstore.

        Args:
            documents (List[Document]: Documents to add to the vectorstore.

        Returns:
            List[str]: List of IDs of the added texts.
        """
        # TODO: Handle the case where the user doesn't provide ids on the Collection
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return self.add_texts(texts, metadatas, **kwargs)

    def get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        query_dict = {"query": {"match": {"content": query}}, "size": self.k}
        response = self.client.search(index=self.index_name, body=query_dict)

        def default_doc_builder(hit: Dict) -> Document:
            return Document(
                page_content=hit["_source"].get(self.query_field, ""),
                metadata=hit["_source"]["metadata"],
            )
        
        doc_builder = default_doc_builder

        result_docs = []
        for r in response["hits"]["hits"]:
            d = Document(page_content=r["_source"]["content"])
            d.metadata.update(r["_source"]["metadata"])
            result_docs.append(d)
        return result_docs