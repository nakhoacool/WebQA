# Guidelines document
This file is served as the guidelines to use the chatbot

# How to add new data

## Proposition RAG bot
Step 1: Pick a dataset that have a proposition list 

- [TDT dataset](https://huggingface.co/datasets/BroDeadlines/TEST.TDT.mini.tdt_copora_data/viewer/compact_diemchuan)
- [UEH dataset](https://huggingface.co/datasets/BroDeadlines/TEST.UEH.ueh_copora_data/viewer/default)

Step 2: Locate to this [file](../core/experiments/do_data/build_data_etl.ipynb)

- Replace DATA_REPO, SUBSET for the picked dataset
- Choose your own value for "INDEX" as id to store on ES
- Start running the code from "Push Proposition dataset to ES"

Done