import pytest

from lsd.parser import parse
from lsd.term import Node, Seq, Span, TermRule, Var


def test_blank():
    assert parse("") == Seq()


def test_str():
    assert parse("test") == "test"
    assert parse("test123") == "test123"


def test_numbers():
    assert parse("123") == 123
    assert parse("1.2") == 1.2


def test_variables():
    assert parse("!x") == Var("x", Span(1, 1))
    assert parse("?x") == Var("x", Span(0, 1))
    assert parse("+x") == Var("x", Span(1, None))
    assert parse("*x") == Var("x", Span(0, None))


def test_simple_nodes():
    # empty node, single-arg, multi-arg
    assert parse("test[]") == Node("test")
    assert parse("test[123]") == Node("test", 123)
    assert parse("test[1 2 3]") == Node("test", 1, 2, 3)
    assert parse("test[a b c]") == Node("test", "a", "b", "c")


def test_nested_nodes():
    term = "a[b[c] d[e[f]]]"
    expected = Node("a", Node("b", "c"), Node("d", Node("e", "f")))
    assert parse(term) == expected


def test_rule_parsing():
    # single rule
    r1 = parse("!A -> x")
    assert isinstance(r1, TermRule)
    assert r1.pattern == Var.from_prefix("!", "A")
    assert r1.rhs == "x"

    # rule with nodes
    r2 = parse("f[1 a] -> g[2 b]")
    expected2 = TermRule(Node("f", 1, "a"), Node("g", 2, "b"))
    assert r2 == expected2

    # nested node rule
    r3 = parse("a[b[c]] -> d[e[f]]")
    expected3 = TermRule(
        Node("a", Node("b", "c")),
        Node("d", Node("e", "f")),
    )
    assert r3 == expected3


def test_rule_nesting():
    # right-associative by default
    r1 = parse("a -> b -> c")
    expected1 = TermRule("a", TermRule("b", "c"))
    assert r1 == expected1

    # explicit grouping
    r2 = parse("a -> (b -> c) -> d")
    expected2 = TermRule("a", TermRule(TermRule("b", "c"), "d"))
    assert r2 == expected2


def test_rule_complex_grouping():
    r = parse("(a -> b) -> (c -> d)")
    expected = TermRule(TermRule("a", "b"), TermRule("c", "d"))
    assert r == expected


def test_invalid_rule_raises():
    with pytest.raises(ValueError):
        parse("A -> ")
