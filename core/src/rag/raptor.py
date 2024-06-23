from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import umap
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sklearn.mixture import GaussianMixture
from src.service.provider import ProviderService
from src.service.applog import AppLogService
from src.utils.text_utils import window_slide_chunks, window_slide_split
# Summarization

# SUMMARIZATION_TEMPLATE = """Give a detailed summary of the documentation provided.
# Documentation:
# {context}
# """

SUMMARIZATION_TEMPLATE = """Hãy tóm tắt văn bản sau một cách ngắn gọn và xúc tích.
Văn bản:
{context}
"""

SUMMARY_SEPARATOR = "------"

class RAPTOR:

    def __init__(self, provider: ProviderService, context_len: int = 2000) -> None:
        self.RANDOM_SEED = 224  # Fixed seed for reproducibility
        self.CONTEXT_LIMIT = context_len # a number of words a text can contains
        self.embd = provider.get_gemini_embeddings()
        self.model = provider.get_simple_gemini_pro()
        self.logger = AppLogService(name="raptor.log")
        return

    ### --- Code from citations referenced above (added comments and docstrings) --- ###


    def global_cluster_embeddings(
        self,
        embeddings: np.ndarray,
        dim: int,
        n_neighbors: Optional[int] = None,
        metric: str = "cosine",
    ) -> np.ndarray:
        """
        Perform global dimensionality reduction on the embeddings using UMAP.

        Parameters:
        - embeddings: The input embeddings as a numpy array.
        - dim: The target dimensionality for the reduced space.
        - n_neighbors: Optional; the number of neighbors to consider for each point.
                    If not provided, it defaults to the square root of the number of embeddings.
        - metric: The distance metric to use for UMAP.

        Returns:
        - A numpy array of the embeddings reduced to the specified dimensionality.
        """
        if n_neighbors is None:
            n_neighbors = int((len(embeddings) - 1) ** 0.5)
        return umap.UMAP(
            n_neighbors=n_neighbors, n_components=dim, metric=metric
        ).fit_transform(embeddings)


    def local_cluster_embeddings(
        self,
        embeddings: np.ndarray, dim: int, num_neighbors: int = 10, metric: str = "cosine"
    ) -> np.ndarray:
        """
        Perform local dimensionality reduction on the embeddings using UMAP, typically after global clustering.

        Parameters:
        - embeddings: The input embeddings as a numpy array.
        - dim: The target dimensionality for the reduced space.
        - num_neighbors: The number of neighbors to consider for each point.
        - metric: The distance metric to use for UMAP.

        Returns:
        - A numpy array of the embeddings reduced to the specified dimensionality.
        """
        return umap.UMAP(
            n_neighbors=num_neighbors, n_components=dim, metric=metric
        ).fit_transform(embeddings)


    def get_optimal_clusters(
        self, embeddings: np.ndarray, max_clusters: int = 50
    ) -> int:
        """
        Determine the optimal number of clusters using the Bayesian Information Criterion (BIC) with a Gaussian Mixture Model.

        Parameters:
        - embeddings: The input embeddings as a numpy array.
        - max_clusters: The maximum number of clusters to consider.
        - random_state: Seed for reproducibility.

        Returns:
        - An integer representing the optimal number of clusters found.
        """
        max_clusters = min(max_clusters, len(embeddings))
        n_clusters = np.arange(1, max_clusters)
        bics = []
        for n in n_clusters:
            gm = GaussianMixture(n_components=n, random_state=self.RANDOM_SEED)
            gm.fit(embeddings)
            bics.append(gm.bic(embeddings))
        return n_clusters[np.argmin(bics)]


    def GMM_cluster(self, embeddings: np.ndarray, threshold: float):
        """
        Cluster embeddings using a Gaussian Mixture Model (GMM) based on a probability threshold.

        Parameters:
        - embeddings: The input embeddings as a numpy array.
        - threshold: The probability threshold for assigning an embedding to a cluster.
        - random_state: Seed for reproducibility.

        Returns:
        - A tuple containing the cluster labels and the number of clusters determined.
        """
        n_clusters = self.get_optimal_clusters(embeddings=embeddings)
        gm = GaussianMixture(n_components=n_clusters, random_state=self.RANDOM_SEED)
        gm.fit(embeddings)
        probs = gm.predict_proba(embeddings)
        labels = [np.where(prob > threshold)[0] for prob in probs]
        return labels, n_clusters


    def perform_clustering(
        self,
        embeddings: np.ndarray,
        dim: int,
        threshold: float,
    ) -> List[np.ndarray]:
        """
        Perform clustering on the embeddings by first reducing their dimensionality globally, then clustering
        using a Gaussian Mixture Model, and finally performing local clustering within each global cluster.

        Parameters:
        - embeddings: The input embeddings as a numpy array.
        - dim: The target dimensionality for UMAP reduction.
        - threshold: The probability threshold for assigning an embedding to a cluster in GMM.

        Returns:
        - A list of numpy arrays, where each array contains the cluster IDs for each embedding.
        """
        if len(embeddings) <= dim + 1:
            # Avoid clustering when there's insufficient data
            return [np.array([0]) for _ in range(len(embeddings))]

        # Global dimensionality reduction
        reduced_embeddings_global = self.global_cluster_embeddings(embeddings, dim)
        # Global clustering
        global_clusters, n_global_clusters = self.GMM_cluster(
            reduced_embeddings_global, threshold
        )

        all_local_clusters = [np.array([]) for _ in range(len(embeddings))]
        total_clusters = 0

        # Iterate through each global cluster to perform local clustering
        for i in range(n_global_clusters):
            # Extract embeddings belonging to the current global cluster
            global_cluster_embeddings_ = embeddings[
                np.array([i in gc for gc in global_clusters])
            ]

            if len(global_cluster_embeddings_) == 0:
                continue
            if len(global_cluster_embeddings_) <= dim + 1:
                # Handle small clusters with direct assignment
                local_clusters = [np.array([0]) for _ in global_cluster_embeddings_]
                n_local_clusters = 1
            else:
                # Local dimensionality reduction and clustering
                reduced_embeddings_local = self.local_cluster_embeddings(
                    global_cluster_embeddings_, dim
                )
                local_clusters, n_local_clusters = self.GMM_cluster(
                    reduced_embeddings_local, threshold
                )

            # Assign local cluster IDs, adjusting for total clusters already processed
            for j in range(n_local_clusters):
                local_cluster_embeddings_ = global_cluster_embeddings_[
                    np.array([j in lc for lc in local_clusters])
                ]
                indices = np.where(
                    (embeddings == local_cluster_embeddings_[:, None]).all(-1)
                )[1]
                for idx in indices:
                    all_local_clusters[idx] = np.append(
                        all_local_clusters[idx], j + total_clusters
                    )

            total_clusters += n_local_clusters

        return all_local_clusters


    ### --- Our code below --- ###


    def embed(self, texts):
        """
        Generate embeddings for a list of text documents.

        This function assumes the existence of an `embd` object with a method `embed_documents`
        that takes a list of texts and returns their embeddings.

        Parameters:
        - texts: List[str], a list of text documents to be embedded.

        Returns:
        - numpy.ndarray: An array of embeddings for the given text documents.
        """
        text_embeddings = []
        for text in texts:
            try:
                # text_embeddings = self.embd.embed_documents(texts, batch_size=2)
                embeddings = self.embd.embed_query(text=text)
                text_embeddings.append(embeddings)
            except:
                print("Error at generate embeddings")
                self.logger.logger.exception(f"[ERROR] {text}")
                if len(text.split(" ")) <= self.CONTEXT_LIMIT:
                    continue
                split_texts = window_slide_split(text=text, step=100, chunk_size=1000)
                for split in split_texts:
                    embeddings = self.embd.embed_query(text=split)
                    text_embeddings.append(embeddings)
        text_embeddings_np = np.array(text_embeddings)
        return text_embeddings_np


    def embed_cluster_texts(self, texts: List[str], list_ids: List[str]):
        """
        Embeds a list of texts and clusters them, returning a DataFrame with texts, their embeddings, and cluster labels.

        This function combines embedding generation and clustering into a single step. It assumes the existence
        of a previously defined `perform_clustering` function that performs clustering on the embeddings.

        Parameters:
        - texts: List[str], a list of text documents to be processed.
        - list_ids: List[str], a list of id corresponding to each input text documents.

        Returns:
        - pandas.DataFrame: A DataFrame containing the original texts, their embeddings, and the assigned cluster labels.
        """
        text_embeddings_np = self.embed(texts)  # Generate embeddings
        cluster_labels = self.perform_clustering(
            text_embeddings_np, 10, 0.1
        )  # Perform clustering on the embeddings
        df = pd.DataFrame()  # Initialize a DataFrame to store the results
        df["text"] = texts  # Store original texts
        df["embd"] = list(text_embeddings_np)  # Store embeddings as a list in the DataFrame
        df["cluster"] = cluster_labels  # Store cluster labels
        df['doc_ids'] = list_ids
        return df


    def fmt_txt(self, df: pd.DataFrame) -> str:
        """
        Formats the text documents in a DataFrame into a single string.

        Parameters:
        - df: DataFrame containing the 'text' column with text documents to format.

        Returns:
        - A single string where all text documents are joined by a specific delimiter.
        """
        unique_txt = df["text"].tolist()
        return f"{SUMMARY_SEPARATOR} \n {SUMMARY_SEPARATOR}".join(unique_txt)


    def embed_cluster_summarize_texts(
        self, texts: List[str], list_ids: List[str], level: int
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Embeds, clusters, and summarizes a list of texts. This function first generates embeddings for the texts,
        clusters them based on similarity, expands the cluster assignments for easier processing, and then summarizes
        the content within each cluster.

        Parameters:
        - texts: A list of text documents to be processed.
        - list_ids: A list of ids corresponding to each input text
        - level: An integer parameter that could define the depth or detail of processing.

        Returns:
        - Tuple containing two DataFrames:
        1. The first DataFrame (`df_clusters`) includes the original texts, their embeddings, and cluster assignments.
        2. The second DataFrame (`df_summary`) contains summaries for each cluster, the specified level of detail,
            and the cluster identifiers.
        """

        # Embed and cluster the texts, resulting in a DataFrame with 'text', 'embd', 'cluster', 'doc_ids' columns
        df_clusters = self.embed_cluster_texts(texts, list_ids=list_ids)

        # Prepare to expand the DataFrame for easier manipulation of clusters
        expanded_list = []

        # Expand DataFrame entries to document-cluster pairings for straightforward processing
        for index, row in df_clusters.iterrows():
            for cluster in row["cluster"]:
                expanded_list.append(
                    {"text": row["text"], "embd": row["embd"], "cluster": cluster, "doc_ids": row['doc_ids']}
                )

        # Create a new DataFrame from the expanded list
        expanded_df = pd.DataFrame(expanded_list)

        # Retrieve unique cluster identifiers for processing
        all_clusters = expanded_df["cluster"].unique()

        print(f"--Generated {len(all_clusters)} clusters--")

        prompt = ChatPromptTemplate.from_template(SUMMARIZATION_TEMPLATE)
        chain = prompt | self.model | StrOutputParser()

        # Format text within each cluster for summarization
        summaries = []
        new_ids = []
        for i in all_clusters:
            df_cluster = expanded_df[expanded_df["cluster"] == i]
            formatted_txt = self.fmt_txt(df_cluster)
            summaries.append(chain.invoke({"context": formatted_txt}))
            new_ids.append(";".join(df_cluster['doc_ids'].tolist()))

        # Create a DataFrame to store summaries with their corresponding cluster and level
        df_summary = pd.DataFrame(
            {
                "summaries": summaries,
                "level": [level] * len(summaries),
                "cluster": list(all_clusters),
                "doc_ids": new_ids 
            }
        )
        return df_clusters, df_summary


    def recursive_embed_cluster_summarize(
        self, texts: List[str], list_ids: List[str], level: int = 1, n_levels: int = 3
    ) -> Dict[int, Tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Recursively embeds, clusters, and summarizes texts up to a specified level or until
        the number of unique clusters becomes 1, storing the results at each level.

        Parameters:
        - texts: List[str], texts to be processed.
        - level: int, current recursion level (starts at 1).
        - n_levels: int, maximum depth of recursion.

        Returns:
        - Dict[int, Tuple[pd.DataFrame, pd.DataFrame]], a dictionary where keys are the recursion
        levels and values are tuples containing the clusters DataFrame and summaries DataFrame at that level.
        """
        results = {}  # Dictionary to store results at each level

        # Perform embedding, clustering, and summarization for the current level
        df_clusters, df_summary = self.embed_cluster_summarize_texts(texts, list_ids=list_ids, level=level)

        # Store the results of the current level
        results[level] = (df_clusters, df_summary)

        # Determine if further recursion is possible and meaningful
        unique_clusters = df_summary["cluster"].nunique()
        if level < n_levels and unique_clusters > 1:
            # Use summaries as the input texts for the next level of recursion
            th_texts = df_summary["summaries"].tolist()
            th_list_ids = df_summary["doc_ids"].tolist()
            new_texts, new_list_ids = self.reduce_text_length(texts=th_texts, ids=th_list_ids)
            next_level_results = self.recursive_embed_cluster_summarize(
                new_texts, new_list_ids, level + 1, n_levels
            )

            # Merge the results from the next level into the current results dictionary
            results.update(next_level_results)

        return results
    
    def reduce_text_length(self, texts: List[str], ids: List[str]):
        """
            Split the long text length for the AI models
        """
        text_list = []
        id_list = []
        for text, id in zip(texts, ids):
            words = len(text.split(" "))
            if words <= self.CONTEXT_LIMIT:
                text_list.append(text)
                id_list.append(id)
                continue
            print(f"[LONG] a text with {words} words: id {id}")
            split_chunks = words % self.CONTEXT_LIMIT
            if split_chunks == 1:
                split_chunks = 2
            split_txts = window_slide_chunks(text=text, step_ratio=0.25, chunks=split_chunks)
            for a in split_txts:
                text_list.append(a)
                id_list.append(id)
        return text_list, id_list

    def test_log(self, msg: str):
        """
            Test logging
        """
        self.logger.logger.exception(msg=msg)
        return