import pytest
from lsd.env import Env
from lsd.match import match_pattern
from lsd.parser import parse, parse_ensure
from lsd.term import Node, Seq, Span, Term, Var


def mp(pat: str | Term, tgt: str | Term) -> Env | None:
    pat = parse_ensure(pat) if isinstance(pat, str) else pat
    tgt = parse_ensure(tgt) if isinstance(tgt, str) else tgt
    return match_pattern(pat, tgt)


def test_literal_and_simple_seq():
    assert mp("x", "x") == Env()
    assert mp("x", "y") is None
    assert mp(1, 1) == Env()
    assert mp(1, 2) is None
    assert mp(Seq("a"), Seq("a")) == Env()
    assert mp(Seq("a"), Seq("b")) is None


def test_splice():
    assert mp("*A x *B", "a x c d") == Env(A=("a",), B=("c", "d"))
    assert mp("*A x *B", "a y c d") is None


def test_var_with_type_guards_and_spread():
    # Testing type guards and spread behavior
    assert mp("?X:int", "a") == Env(X=())
    assert mp("!X:int", "a") is None
    assert mp("*X:int", "a") == Env(X=())
    assert mp("+X:int", "a") is None
    assert mp("?X:str", "a") == Env(X=("a",))
    assert mp("!X:str", "a") == Env(X=("a",))
    assert mp("*X:str", "a") == Env(X=("a",))
    assert mp("+X:str", "a") == Env(X=("a",))


def test_explicit_guard_matching():
    assert mp("!A:int", "a") is None
    assert mp("!A:int", 1) == Env(A=(1,))
    assert mp("!A:str", 1) is None
    assert mp("!A:str", "a") == Env(A=("a",))
    assert mp("!A:X", Node("Y", 123)) is None
    assert mp("!A:X", Node("X", 123)) == Env(A=(Node("X", 123),))
    assert mp("?A:X", Node("Y", 123)) == Env(A=())


def test_optional_and_spread_empty():
    x = Var("x", Span(0, 1))
    assert mp(Seq(x), Seq()) == Env(x=())

    xs = Var("xs", Span(0, None))
    assert mp(Seq(1, xs, 2), Seq(1, 2)) == Env(xs=())


def test_single_and_repeated_vars():
    assert mp("!X", "a") == Env(X=("a",))


def test_repeated_vars():
    assert mp("!A !A", "x x") == Env(A=("x",))
    assert mp("!A !A", "x y") is None
    assert mp("!A !B", "x y") == Env(A=("x",), B=("y",))


def test_spread_patterns():
    assert mp("*A", "x y") == Env(A=Seq("x", "y"))
    assert mp("*A !B", "e f g") == Env(A=("e", "f"), B=("g",))
    assert mp("!A !B *S", "x y 1 2 3") == Env(A=("x",), B=("y",), S=(1, 2, 3))
    assert mp("*A x *B", "a x c d") == Env(A=("a",), B=("c", "d"))


def test_seq_and_node_consistency():
    x = Var("x")
    assert mp(Seq(x, x), Seq(1, 1)) == Env(x=(1,))
    assert mp(Seq(x, x), Seq(1, 2)) is None

    assert mp(Node("f", Var("x"), 2), Node("f", 1, 2)) == Env(x=(1,))
    pat = Node("wrap", Var("x"), Node("const", Var("y")))
    tgt = Node("wrap", 1, Node("const", 2))
    assert mp(pat, tgt) == Env(x=(1,), y=(2,))


def test_misc_spread_combinations():
    assert mp("*X !Y", "a b c") == Env(X=("a", "b"), Y=("c",))
    assert mp("*X c !Z", "a b c d") == Env(X=("a", "b"), Z=("d",))
    assert mp("*X c *Z", "a b c d e") == Env(X=("a", "b"), Z=("d", "e"))


def test_pmatch_x_x():
    assert mp("x", "x") == Env()
    assert mp("x", "y") is None
    assert mp(Var("A"), Var("A")) == Env()
    assert mp(Var("A"), "x") == Env(A=("x",))
    assert mp(Seq(Var("A"), Var("B")), Seq("x", "y")) == Env(A=("x",), B=("y",))


@pytest.mark.skip("TODO")
def test_pmatch_splice_a_x_c_d():
    assert mp("*A x *B", "a x c d") == Env(A=("a",), B=("c", "d"))
    assert mp("*A x *B", "a y c d") is None


def test_pmatch_splice_a_b_s_e_q_c_d():
    assert mp(
        Seq(
            Var("A"),
            Var("B"),
            Var("S", Span(0, None)),
            Var("C"),
            Var("D"),
        ),
        Seq(
            "a",
            "b",
            "s",
            "e",
            "q",
            "c",
            "d",
        ),
    ) == Env(
        A=("a",),
        B=("b",),
        S=("s", "e", "q"),
        C=("c",),
        D=("d",),
    )


def test_wildcard():
    """
    Test that the wildcard term (`_`) matches any sequence.
    """
    # Here, `_` should match any part of the sequence.
    assert mp("_ x y z", "1 x y z") == Env()
    assert mp("_ a b c", "z a b c") == Env()
    assert mp("_", "anything") == Env()
    assert mp("_ x y", "a x y") == Env()
