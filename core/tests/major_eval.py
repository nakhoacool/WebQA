from pandas import DataFrame
import os
import pandas as pd
from datetime import datetime

def test_major(qa_df: DataFrame, ques_col: str, retriever, error_limit: int = 20):
    correct = 0
    total = 0
    err = 0
    for id, row in qa_df.iterrows():
        query = row[ques_col]
        ground_result = int(row['doc_id'])
        total += 1
        try:
            res = retriever.get_relevant_documents(query)
            for idx, r in enumerate(res):
                target_id = int(r.metadata['id'])
                if target_id == ground_result:
                    correct += 1
                    break
        except:
            err += 1
            if err == error_limit:
                break
            print(query)
    return [correct,total]


class MajorBlogPostEvaluation:

    def __init__(self, root_path:str = "./", save_path:str = "./") -> None:
        self.save_path = save_path
        self.root_path = root_path
        self.data_folder = os.path.join(self.root_path, "data/test_major/") 
        pass

    def _eval_retriever(self, file_name: str, target_file: str, ques_col: str, retriever, metadata):
        df = pd.read_csv(os.path.join(self.data_folder, target_file))
        START = datetime.now()
        correct, total = test_major(df, ques_col, retriever, error_limit=20)
        END = datetime.now()
        with open(os.path.join(self.save_path, file_name), "a") as f:
            f.write("\n->\n")
            f.write(f"Start: {START}\n")
            [f.write(f"Param {k}: {v}\n") for k, v in metadata.items()]
            f.write(f"Correct: {str(correct)}\n")
            f.write(f"Total: {str(total)}\n")
            f.write(f"Score: {str(correct/total)}\n")
            f.write(f"End: {END}\n")
        return
    
    def eval_sample(self, file_name: str, retriever, metadata):
        self._eval_retriever(file_name=file_name, 
                             target_file="sample_test_case.csv", 
                             ques_col="public question", retriever=retriever, 
                              metadata=metadata)
        return

    def eval_public(self, file_name: str, retriever, metadata):
        self._eval_retriever(file_name=file_name, 
                             target_file="public_test_case.csv", 
                             ques_col="public question", retriever=retriever, 
                              metadata=metadata)
        return
    
    def eval_private_hard(self, file_name: str, retriever, metadata):
        self._eval_retriever(file_name=file_name, 
                             target_file="hard_private_test_case.csv", 
                             ques_col="private question", retriever=retriever, 
                              metadata=metadata)
        return

    def eval_private(self, file_name: str, retriever, metadata):
        self._eval_retriever(file_name=file_name, 
                             target_file="private_test_case.csv", 
                             ques_col="private question", retriever=retriever, 
                              metadata=metadata)
        return
    
