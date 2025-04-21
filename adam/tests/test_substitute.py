import pytest

from lsd.env import Env
from lsd.substitute import substitute
from lsd.term import Node, Seq, Var


def test_substitute_single_variable():
    env = Env(A=("x",), B=("y",))
    assert substitute(Var("A"), env) == "x"


def test_substitute_sequence_of_variables():
    env = Env(A=("x",), B=("y",))
    assert substitute(Seq(Var("A"), Var("B")), env) == Seq("x", "y")


def test_substitute_node_with_variable_head():
    env = Env(A=("x",), B=("y",))
    # Node(head=Var("A"))  → Node(head="x")
    assert substitute(Node(Var("A")), env) == Node("x")


def test_substitute_seq_single_variable():
    env = Env(A=("x",), B=("y",))
    assert substitute(Seq(Var("A")), env) == Seq("x")


def test_optional_variable_unbound_returns_empty():
    env = Env(A=("x",), B=("y",))
    empty_opt = Var.from_prefix("?", "Z")
    # unbound optional ?Z → Seq()
    assert substitute(Seq(empty_opt), env) == Seq()


def test_spread_variable_with_single_element():
    # spread S bound to Seq("a","b","c")
    env1 = Env(S=Seq("a", "b", "c"))
    assert substitute(Var("S"), env1) == Seq("a", "b", "c")

    # spread X bound to Seq("abc")
    env2 = Env(X=Seq("abc"))
    assert substitute(Var("X"), env2) == Seq("abc")


def test_optional_variable_with_value():
    env = Env(Z=Seq("value"))
    opt_z = Var.from_prefix("?", "Z")
    assert substitute(Seq(opt_z), env) == Seq("value")


def test_optional_variable_with_no_value():
    # unbound optional Z → empty
    assert substitute(Seq(Var.from_prefix("?", "Z")), Env()) == Seq()


def test_seq_with_optional_and_required():
    env = Env(A=Seq("x"), B=Seq("y"))
    opt_a = Var.from_prefix("?", "A")
    req_b = Var("B")
    assert substitute(Seq(opt_a, req_b), env) == Seq("x", "y")


def test_sequence_with_multiple_optional_vars():
    env = Env(A=Seq("x"), B=Seq("y"))
    opt_a = Var.from_prefix("?", "A")
    opt_b = Var.from_prefix("?", "B")
    assert substitute(Seq(opt_a, opt_b), env) == Seq("x", "y")


def test_unbound_variable_raises_key_error():
    with pytest.raises(KeyError):
        substitute(Seq(Var("Z")), Env())


def test_spread_variable_multiple_elements_error():
    env = Env(X=("x", "y"))
    with pytest.raises(ValueError):
        substitute(Var("X"), env)
