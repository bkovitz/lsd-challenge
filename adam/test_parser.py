import unittest
from parser import parse

from term import Node, Rule, Term, Var, node


class TestParser(unittest.TestCase):

    def assertParse(self, text: str, expect: Term):
        self.assertEqual(parse(text), expect)

    def test_symbol(self):
        self.assertParse("test", "test")

    def test_dollar(self):
        self.assertParse("$test", "$test")

    def test_number(self):
        self.assertParse("123", 123)

    def test_var(self):
        self.assertParse("!x", Var("x", none=False, many=False))
        self.assertParse("?x", Var("x", none=True, many=False))
        self.assertParse("+x", Var("x", none=False, many=True))
        self.assertParse("*x", Var("x", none=True, many=True))

    def test_node(self):
        self.assertParse("Seq", "Seq")
        self.assertParse("Seq[]", node("Seq"))
        self.assertParse("test[123]", node("test", 123))
        self.assertParse("test[1 2 3]", node("test", 1, 2, 3))
        self.assertParse("test[a b c]", node("test", "a", "b", "c"))

    def test_nested_nodes(self):
        self.assertParse(
            "a[b[c] d[e]]",
            node("a", node("b", "c"), node("d", "e")),
        )
        self.assertParse(
            "outer[inner1[a] inner2[b[c] d]]",
            node(
                "outer",
                node("inner1", "a"),
                node("inner2", node("b", "c"), "d"),
            ),
        )

    def test_rule(self):
        self.assertParse(
            "!A -> x",
            Rule(Var("A"), "x"),
        )
        self.assertParse(
            "f[1 x] -> g[x]",
            Rule(node("f", 1, "x"), node("g", "x")),
        )
        self.assertParse(
            "Lhs[arg1 $Succ[A] !ARG2] -> Rhs[!ARG2 xyz]",
            Rule(
                node("Lhs", "arg1", "$Succ[A]", Var("ARG2")),
                node("Rhs", Var("ARG2"), "xyz"),
            ),
        )

    def test_deeply_nested_node(self):
        self.assertParse(
            "root[sub1[sub2[sub3[x]]]]",
            node("root", node("sub1", node("sub2", node("sub3", "x")))),
        )

    def test_invalid_rule(self):
        with self.assertRaises(ValueError):
            parse("A -> ")


if __name__ == "__main__":
    unittest.main()
