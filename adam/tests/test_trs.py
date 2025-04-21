import pytest
from lsd.method import Method, MethodRule, Succ
from lsd.parser import parse
from lsd.term import Node, Seq, Span, Var
from lsd.trs import TermRewriteSystem


@pytest.fixture
def engine():
    return TermRewriteSystem()


def test_basic_var_rule(engine):
    X = Var("X")
    engine.add_rule(Node("Foo", X), Node("Bar", X))
    for letter in iter("amt"):
        assert engine.rewrite(Node("Foo", letter)) == Node("Bar", letter)


def test_successive_spread_rules(engine):
    engine.add_rule(parse("Last[*A !X]"), parse("!X"))
    engine.add_rule(parse("*A m *B"), parse("*B n *A"))
    assert engine.rewrite(Node("Last", "a", "b", "c")) == "c"
    assert engine.rewrite(Seq(*"xyzmabc")) == Seq(*"abcnxyz")


def test_front(engine):
    engine.add_method(Method("Front", exec=lambda args: args[:2]))
    assert engine.rewrite(parse("Front[abc]")) == "ab"


def test_advance_last_rule(engine):
    engine.add_method(
        Method("AdvanceLast", exec=lambda args: args[:-1] + Succ(args[-1])),
    )
    assert engine.rewrite(parse("AdvanceLast[abc]")) == parse("abd")


def test_basic_no_match(engine):
    engine.add_rule(Node("Abc", "a"), "b")
    engine.add_rule(Node("A", "x"), "y")
    assert engine.rewrite(Node("Abc", "a")) == "b"
    assert engine.rewrite(Node("A", "x")) == "y"
    # no match
    assert engine.rewrite(Node("Abc", "b")) == Node("Abc", "b")
    assert engine.rewrite(Node("B", "x")) == Node("B", "x")
    assert engine.rewrite("NoMatchingRule") == "NoMatchingRule"


@pytest.mark.parametrize(
    "input_term, expected",
    [
        # flattening nested Succ rules in a Seq
        (
            Seq("c", Node("Succ", "b"), Node("Succ", Node("Succ", "a"))),
            Seq("c", "c", "c"),
        ),
        # same inside a Node body
        (
            Node("Box", "c", Node("Succ", "b"), Node("Succ", Node("Succ", "a"))),
            Node("Box", "c", "c", "c"),
        ),
    ],
)
def test_multistep_nested(input_term, expected, engine):
    engine.add_rule(Node("Succ", "a"), "b")
    engine.add_rule(Node("Succ", "b"), "c")
    assert engine.rewrite(input_term) == expected


def test_sequence_flattening(engine):
    x = Var("X")
    engine.add_rule(Node("Inner", x), x)
    nested = Node("Outer", Node("Inner", "a"))
    assert engine.rewrite(nested) == Node("Outer", "a")


def test_method_rule(engine):
    engine.add_rule(MethodRule(Method("Abc", lambda s: "d")))
    engine.add_rule(MethodRule(Method("Upper", lambda s: s.upper())))
    engine.add_rule(MethodRule(Method("Lower", lambda s: s.lower())))
    engine.add_rule(MethodRule(Method("Split", lambda s: Seq(*s))))
    assert engine.rewrite(Node("Abc", "abc")) == "d"
    assert engine.rewrite(Node("Upper", "hello")) == "HELLO"
    assert engine.rewrite(Node("Lower", "HELLO")) == "hello"
    assert engine.rewrite(Node("Split", "abc")) == Seq("a", "b", "c")


def test_rule_priority(engine):
    # later additions override earlier ones
    Xa = Node("X", "a")
    engine.add_rule(Xa, "first")
    engine.add_rule(Xa, "second")
    assert engine.rewrite(Xa) == "second"


def test_seq_splicing(engine):
    # Seq[X] -> X flattens a Seq-of-Seq
    x = Var("X")
    engine.add_rule(Seq(x), x)
    inp = Seq(Seq("a", Seq("b", Seq())), "c")
    assert engine.rewrite(inp) == Seq("a", "b", "c")


@pytest.mark.skip("TODO")
def test_new_world_method(engine):
    engine.add_method(Method("NewWorld", lambda _: Node("NewWorld", "abd")))
    assert engine.rewrite(Node("NewWorld", "abc", "Blank")) == Node("NewWorld", "abd")


def test_trace(engine: TermRewriteSystem):
    engine.rewrite(Node("Succ", "a"))
    assert len(engine.trace) == 1


def test_rewrite_succ(engine):
    assert engine.rewrite(Node("Succ", "a")) == "b"


def test_rewrite_with_vars(engine):
    engine.add_rule(
        Seq(
            Var("A"),
            "x",
            Var("S", Span(0, None)),
        ),
        Node(
            "GotIt",
            Var("S", Span(0, None)),
            Var("A"),
        ),
    )
    assert engine.rewrite(Seq("a", "x", "b", "c")) == Node("GotIt", "b", "c", "a")
