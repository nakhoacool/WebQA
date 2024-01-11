import pandas as pd

def load_csv_and_split_to_docs(csv_path:str, sp):
    """
        This function load csv and split it into documents.
    """
    df = pd.read_csv(csv_path)
    return