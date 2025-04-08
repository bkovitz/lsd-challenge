import unittest
from parser import parse

from term import Rule, Term, Var, node


class TestParser(unittest.TestCase):

    def assertParse(self, text: str, expect: Term):
        """Assert that parsing a text string produces the expected Term.

        Args:
            text: The input string to parse (e.g., '!x', 'Seq[a b]').
            expect: The expected Term object (e.g., Var, Node, or literal).
        """
        self.assertEqual(parse(text), expect)

    def test_symbol(self):
        """Test parsing a simple symbol."""
        self.assertParse("test", "test")

    def test_dollar(self):
        """Test parsing a dollar-prefixed symbol."""
        self.assertParse("$test", "$test")

    def test_number(self):
        """Test parsing a numeric literal."""
        self.assertParse("123", 123)

    def test_var(self):
        """Test parsing different variable notations."""
        self.assertParse("!x", Var("x", none=False, many=False))  # Standard var
        self.assertParse("?x", Var("x", none=True, many=False))  # Optional var
        self.assertParse("+x", Var("x", none=False, many=True))  # Non-empty spread
        self.assertParse("*x", Var("x", none=True, many=True))  # Optional spread

    def test_node(self):
        """Test parsing Node structures with and without arguments."""
        self.assertParse("Seq", "Seq")  # Bare symbol
        self.assertParse("Seq[]", node("Seq"))  # Empty node
        self.assertParse("test[123]", node("test", 123))  # Single arg
        self.assertParse("test[1 2 3]", node("test", 1, 2, 3))  # Multiple numbers
        self.assertParse("test[a b c]", node("test", "a", "b", "c"))  # Multiple symbols

    def test_nested_nodes(self):
        """Test parsing nested Node structures."""
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
        """Test parsing Rule objects from strings."""
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
        """Test parsing a deeply nested Node structure."""
        self.assertParse(
            "root[sub1[sub2[sub3[x]]]]",
            node("root", node("sub1", node("sub2", node("sub3", "x")))),
        )

    def test_invalid_rule(self):
        """Test parsing an incomplete rule raises an error."""
        with self.assertRaises(ValueError):
            parse("A -> ")


if __name__ == "__main__":
    unittest.main()
