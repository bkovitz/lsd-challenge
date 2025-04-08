import unittest

from env import Env
from substitute import substitute
from term import Node, Seq, Term, Var


class TestSubstitute(unittest.TestCase):

    def setUp(self) -> None:
        self.env = Env(A=Seq("x"), B=Seq("y"))

    def assertSubstitution(self, term: Term, expect: Term) -> None:
        self.assertEqual(substitute(term, self.env), expect)

    def test_var(self) -> None:
        """Test substitution of a single variable with its value from the environment."""
        self.assertSubstitution(Var("A"), "x")

    def test_var_seq(self) -> None:
        """Test substitution of a sequence of variables with their corresponding values."""
        self.assertSubstitution(
            (Var("A"), Var("B")),
            ("x", "y"),
        )

    def test_node_head(self) -> None:
        """Test substitution of a variable in a node's head position."""
        self.assertSubstitution(
            Node(Var("A")),
            Node("x"),
        )

    def test_node_body(self) -> None:
        """Test substitution of a variable within a node's body sequence."""
        self.assertSubstitution(
            Node("Seq", (Var("A"),)),
            Node("Seq", ("x",)),
        )

    def test_unbound_variable(self) -> None:
        with self.assertRaises(KeyError):
            substitute(Seq((Var("Z"),)), self.env)
