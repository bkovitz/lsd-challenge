from lsd.method import Method, Pred, Reverse, Rotate2ThenReverse, Succ, TripleSucc


def test_succ_pred():
    assert Succ("a") == "b"
    assert Pred("z") == "y"
    # non-letters return None
    assert Succ("notachar") is None
    assert Pred("notachar") is None


def test_compose():
    SuccSucc = Method.compose(Succ, Succ)
    SuccPred = Method.compose(Succ, Pred)
    PredPred = Method.compose(Pred, Pred)

    assert SuccSucc("a") == "c"
    assert SuccPred("b") == "b"
    assert PredPred("c") == "a"

    assert SuccSucc.name == "Succ.Succ"
    assert SuccPred.name == "Succ.Pred"
    assert PredPred.name == "Pred.Pred"


def test_composed_methods():
    assert Rotate2ThenReverse("abc") == "acb"
    assert TripleSucc("a") == "d"


def test_repeat():
    triple = Succ.repeat(3)
    assert triple("a") == "d"
    assert Succ.repeat(6)("a") == "g"


def test_method_call():
    # basic calls
    assert Succ("a") == "b"
    assert Pred("b") == "a"
    assert Reverse("abc") == "cba"
