from src.utils import eval_utils


def test_precision_at_ith():
    target = "d4"
    ids = ["d12", "d123", "d4", "d57", "d157", "d157", "d4", "d157", "d4", "d157"]
    a_3 = eval_utils.precision_ith_doc(ith=3, target_id=target, ids=ids)
    assert(a_3 > 0.32 and a_3 < 0.34)
    a_5 = eval_utils.precision_ith_doc(ith=5, target_id=target, ids=ids)
    assert(a_5 > 0.19 and a_5 < 0.211)
    a_8 = eval_utils.precision_ith_doc(ith=8, target_id=target, ids=ids)
    assert(a_8 > 0.24 and a_8 < 0.251)


def test_doc_precisions():
    target = "a"
    ids = ['a', "b", "a", 'd']
    a = eval_utils.retrieved_precisions(target_id=target, ids=ids)
    assert(len(a) == 2)
    assert(a[0] == 1)
    assert(a[1] > 0.32 and a[1] < 0.34)