from typing import List, TypedDict
import json

class EvaluateIR(TypedDict):
    relevant: int
    precision: float
    recall: float
    map_score: float


def precision_ith_doc(ith: int, target_id: str, ids: List[str]) -> float:
    '''
        Calculate the precision of i th relevant document
    '''
    return ids[:ith].count(target_id) / ith

def retrieved_precisions(target_id: str, ids: List[str]) -> List[float]:
    '''
        Calculate precision of each retrieved documents
    '''
    results = []
    i = 1
    totals = len(ids)
    for d in ids:
        if d == target_id:
            results.append(1 / i)
        i += 1
    return results


def evaluate_IR(eval_dataset) -> EvaluateIR:
    '''
        Auto evaluate IR results

        @param eval_dataset (follow: "BroDeadlines/EVAL.IR_evaluation")
    '''
    null_rows = 0 # handle empty evaluation row
    fin_result: EvaluateIR = {}
    num_relevant_retrieved = 0
    num_retrieved = 0
    num_relevant = 0
    re_docs = {}
    precision_list = []
    for row in eval_dataset:
        if len(row['evaluation']) == 0:
            # handle empty evaluation row
            print("nothing to evaluate")
            null_rows += 1
            continue
        target_id = row['doc_id']
        shards = json.loads(row['metadata'])['shards']
        num_relevant += shards
        re_doc_ids = []
        for d in row['evaluation']:
            re_doc_ids.append(d['doc_id'])
            if d['doc_id'] not in re_docs:
                re_docs[d['doc_id']] = 1
            if d['doc_id'] == target_id:
                num_relevant_retrieved += 1
        tmp = retrieved_precisions(target_id=target_id, ids=re_doc_ids)
        if len(tmp) == 0:
            precision_list.append(0)
        else:
            precision_list.append(sum(tmp) / len(tmp))
    num_retrieved = len(re_docs)
    # calculate
    fin_result['relevant'] = num_relevant_retrieved / (eval_dataset.num_rows - null_rows)
    fin_result['precision'] = num_relevant_retrieved / num_retrieved
    fin_result['recall'] = num_relevant_retrieved / num_relevant
    fin_result['map_score'] = sum(precision_list) / (eval_dataset.num_rows - null_rows)
    return fin_result