import pandas as pd
from src.utils.type_utils import create_langchain_doc

class UtilsRAPTOR:

    def __init__(self) -> None:
        pass

    @staticmethod
    def assign_level_id(raptor_tree):
        levels = raptor_tree.keys()
        for level in levels:
            raptor_tree[level][0]['level_id'] = f"tree_{level}"
            raptor_tree[level][1]['level_id'] = f"tree_{level}"
        return

    @staticmethod
    def print_raptor_info(results):
        print(results.keys())
        for i in results.keys():
            print("=======")
            print(len(results[i]))
            print(results[i][0].keys())
            print(results[i][0]['level_id'].unique())
            print(results[i][1].keys())
        return

    @staticmethod
    def flatten_tree(raptor_tree):
        clusters = []
        summarizes = []
        for level in raptor_tree.keys():
            clusters.append(raptor_tree[level][0])
            summarizes.append(raptor_tree[level][1])
        return pd.concat(clusters), pd.concat(summarizes)
    

    @staticmethod
    def collect_data_tree(raptor_tree, leaf_texts, leaf_ids):
        all_texts = [create_langchain_doc(txt, {"doc_id": id}) for txt, id in zip(leaf_texts, leaf_ids)]
        
        # Iterate through the results to extract summaries from each level and add them to all_texts
        for level in sorted(raptor_tree.keys()):
            # Extract summaries from the current level's DataFrame
            summaries = raptor_tree[level][1]["summaries"].tolist()
            d_ids = raptor_tree[level][1]['doc_ids'].tolist()
            # Extend all_texts with the summaries from the current level
            all_texts.extend([create_langchain_doc(txt, {"doc_id": id}) for txt, id in zip(summaries, d_ids)])
        return all_texts