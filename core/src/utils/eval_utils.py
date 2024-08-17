from typing import List, TypedDict
import json
from nltk.translate.bleu_score import sentence_bleu
from rouge_score import rouge_scorer
import numpy as np

class EvaluateIR(TypedDict):
    relevant: int
    precision: float
    recall: float
    map_score: float
    relevant_retrieved: int
    num_retrieved: int
    nulls: int

class EvalBLEU(TypedDict):
    BLEU_4_avg: float
    BLEU_4_median: float
    BLEU_median: float
    BLEU_avg: float

class EvalROUGE(TypedDict):
    ROUGE_L_precision_avg: float
    ROUGE_L_precision_median: float
    ROUGE_L_recall_avg: float
    ROUGE_L_recall_median: float
    ROUGE_L_fmeasure_avg: float
    ROUGE_L_fmeasure_median: float
class QA(TypedDict):
    repo: str
    split: str
    size: int

class ES(TypedDict):
    text_idx: str
    vec_idx: str
    size: int

def calculate_BLEU(grounds: List[str], preds: List[str]) -> EvalBLEU:
    """
        Calculate BLEU score for QA
    """
    total_s4 = []
    total_s1 = []
    for ground, res in zip(grounds, preds):
        if len(ground) == 0 or len(res) == 0:
            continue
        reference = [ground.strip().split(" ")]
        candidate = res.strip().split(" ")
        score4 = sentence_bleu(reference, candidate)
        score1 = sentence_bleu(reference, candidate, weights=(1, 0, 0, 0))
        total_s4.append(score4)
        total_s1.append(score1)
    total_s4 = np.array(total_s4)
    total_s1 = np.array(total_s1)
    result: EvalBLEU = {}
    result['BLEU_4_avg'] = round(total_s4.mean(), 3)
    result['BLEU_4_median'] = round(np.median(total_s4), 3)
    result['BLEU_avg'] = round(total_s1.mean(), 3)
    result['BLEU_median'] = round(np.median(total_s1), 3)
    return result

def calculate_ROUGE(grounds: List[str], preds: List[str]) -> EvalROUGE:
    """
        Calculate ROUGE score
    """
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    preps = []
    recalls = []
    f_scs = []
    for ground, res in zip(grounds, preds):
        scores = scorer.score(ground, res)['rougeL']
        preps.append(scores.precision)
        recalls.append(scores.recall)
        f_scs.append(scores.fmeasure)
    preps = np.array(preps)
    recalls = np.array(recalls)
    f_scs = np.array(f_scs)
    results: EvalROUGE = {}
    results['ROUGE_L_precision_avg'] = round(preps.mean(), 3)
    results['ROUGE_L_precision_median'] = round(np.median(preps), 3)
    results['ROUGE_L_recall_avg'] = round(recalls.mean(), 3)
    results['ROUGE_L_recall_median'] = round(np.median(recalls), 3)
    results['ROUGE_L_fmeasure_avg'] = round(f_scs.mean(), 3)
    results['ROUGE_L_fmeasure_median'] = round(np.median(f_scs), 3)
    return results

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
    for d in ids:
        if d == target_id:
            results.append(1 / i)
        i += 1
    return results


def retrieved_precisions_RAPTOR(target_id: str, ids: List[str]) -> List[float]:
    '''
        Calculate precision of each retrieved documents
    '''
    results = []
    i = 1
    totals = len(ids)
    for d in ids:
        if d == target_id:
            results.append(1 / i)
        elif ";" in d and target_id in d: # for RAPTOR
            results.append(1 / i)
        i += 1
    return results

def evaluate_IR(eval_dataset, limit_k: int = -1, shard_key='shards') -> EvaluateIR:
    '''
        Auto evaluate IR results

        @param eval_dataset (follow: "BroDeadlines/EVAL.IR_evaluation")
        @param limit_k (limit the number of evaluation rows)
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
        shards = json.loads(row['metadata'])[shard_key]
        num_relevant += shards
        re_doc_ids = []
        iter_num = 0
        for d in row['evaluation']:
            re_doc_ids.append(d['doc_id'])
            if d['doc_id'] not in re_docs:
                re_docs[d['doc_id']] = 1
            if d['doc_id'] == target_id:
                num_relevant_retrieved += 1
            iter_num += 1 # limit the number of evaluation rows
            if limit_k > 0 and iter_num >= limit_k:
                break
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
    fin_result['relevant_retrieved'] = num_relevant_retrieved
    fin_result['num_retrieved'] = num_retrieved
    return fin_result

def evaluate_IR_RAPTOR(eval_dataset, limit_k: int = -1, shard_key: str = 'hard_shards') -> EvaluateIR:
    '''
        Auto evaluate IR results of RAPTOR tree

        @param eval_dataset (follow: "BroDeadlines/EVAL.IR_evaluation")
        @param limit_k (limit the number of evaluation rows)
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
        if shard_key in row:
            shards = row[shard_key]
        else:
            shards = json.loads(row['metadata'])[shard_key]
        num_relevant += shards
        re_doc_ids = []
        iter_num = 0
        for d in row['evaluation']:
            re_doc_ids.append(d['doc_id'])
            if d['doc_id'] not in re_docs:
                re_docs[d['doc_id']] = 1
            if target_id in d['doc_id']:
                num_relevant_retrieved += 1
            iter_num += 1 # limit the number of evaluation rows
            if limit_k > 0 and iter_num >= limit_k:
                break
        tmp = retrieved_precisions_RAPTOR(target_id=target_id, ids=re_doc_ids)
        if len(tmp) == 0:
            precision_list.append(0)
        else:
            precision_list.append(sum(tmp) / len(tmp))
    num_retrieved = len(re_docs)
    # calculate
    fin_result['relevant'] = num_relevant_retrieved / (eval_dataset.num_rows - null_rows)
    fin_result['precision'] = round(num_relevant_retrieved / num_retrieved, 3)
    fin_result['recall'] = round(num_relevant_retrieved / num_relevant, 3)
    fin_result['map_score'] = round(sum(precision_list) / (eval_dataset.num_rows - null_rows), 3)
    fin_result['relevant_retrieved'] = num_relevant_retrieved
    fin_result['num_retrieved'] = num_retrieved
    return fin_result