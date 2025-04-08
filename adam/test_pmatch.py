import unittest
from parser import parse

from env import Env
from pmatch import pmatch
from term import Node, Seq, Symbol, Term, Var, node


class TestPMatch(unittest.TestCase):
    def assertMatch(
        self,
        pattern: Term | str,
        target: Term | str,
        expected_env: Env | dict | None = None,
    ) -> None:
        """Assert that pattern matches target and produces the expected environment.

        Args:
            pattern: The pattern term or string to match (e.g., 'Seq[!A *S]').
            target: The target term or string to match against (e.g., 'Seq[x y z]').
            expected_env: The expected bindings (as Env, dict, or None if no match).
        """
        # Parse if str
        lhs = parse(pattern) if isinstance(pattern, str) else pattern
        rhs = parse(target) if isinstance(target, str) else target

        # Convert to Env if dict
        if isinstance(expected_env, dict):
            expected_env = Env(expected_env)

        result = pmatch(lhs, rhs)

        if expected_env is None:
            self.assertIsNone(result, f"Expected no match, but got {result}")
        else:
            self.assertIsInstance(result, Env)
            assert result is not None  # Type hint for mypy
            self.assertEqual(Env(result), expected_env)

    def test_exact_symbols(self) -> None:
        """Test matching identical and differing symbols.

        Verifies that two identical Symbol terms match with an empty environment,
        and two different Symbol terms do not match.
        """
        self.assertEqual(pmatch(Symbol("x"), Symbol("x")), Env())
        self.assertIsNone(pmatch(Symbol("x"), Symbol("y")))

    def test_var_to_symbol(self) -> None:
        """Test binding a variable to a symbol.

        Ensures a Var matches a Symbol and binds the variable to the symbol's value.
        """
        result = pmatch(Var("X"), "a")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["X"], Symbol("a"))

    def test_nested_expr(self) -> None:
        """Test matching a nested expression with a variable.

        Checks that a Node with a variable matches a Node with a symbol,
        binding the variable correctly.
        """
        pattern = Node("Wrap", (Var("A"),))
        target = Node("Wrap", (Symbol("v"),))
        result = pmatch(pattern, target)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result["A"], Symbol("v"))

    def test_complex_sequence(self) -> None:
        """Test matching a complex sequence with multiple variables and a spread.

        Verifies that a sequence with single and spread variables matches
        a target sequence, producing the correct bindings.
        """
        self.assertMatch(
            "Seq[!A !B *S !C !D]",
            "Seq[x y 1 2 3 z t]",
            {
                "A": "x",
                "B": "y",
                "S": Seq((1, 2, 3)),
                "C": "z",
                "D": "t",
            },
        )

    def test_x_x(self) -> None:
        """Test matching two identical simple terms.

        Ensures that two identical symbols match with an empty environment.
        """
        self.assertMatch("x", "x", {})

    def test_x_y(self) -> None:
        """Test mismatching two different simple terms.

        Verifies that two different symbols do not match.
        """
        self.assertMatch("x", "y", None)

    def test_A_A(self) -> None:
        """Test matching two identical variables.

        Ensures that two identical Var terms match with an empty environment.
        """
        self.assertMatch("!A", "!A", {})

    def test_A_x(self) -> None:
        """Test binding a variable to a symbol.

        Checks that a Var matches a symbol and binds it in the environment.
        """
        self.assertMatch("!A", "x", {"A": "x"})

    def test_seq_vars(self) -> None:
        """Test matching a sequence with two variables.

        Verifies that a Seq with two Vars matches a Seq with two symbols.
        """
        self.assertMatch("Seq[!A !B]", "Seq[x y]", {"A": "x", "B": "y"})

    def test_A_A_x_x(self) -> None:
        """Test matching repeated variables with consistent values.

        Ensures that a repeated Var in a Seq matches identical symbols.
        """
        self.assertMatch("Seq[!A !A]", "Seq[x x]", Env({"A": "x"}))

    def test_A_A_x_y(self) -> None:
        """Test mismatching repeated variables with inconsistent values.

        Verifies that a repeated Var in a Seq fails to match different symbols.
        """
        self.assertMatch("Seq[!A !A]", "Seq[x y]", None)

    def test_splice(self) -> None:
        """Test matching a spread variable in a sequence.

        Checks that a spread Var (*A) captures all elements in a Seq.
        """
        self.assertMatch("Seq[*A]", "Seq[x y]", {"A": Seq(("x", "y"))})

    def test_splice_empty(self) -> None:
        """Test matching an empty sequence with a spread variable.

        Ensures that a spread Var (*A) can bind to an empty Seq.
        """
        self.assertMatch("Seq[*A]", "Seq[]", {"A": Seq()})

    def test_splice_with_var(self) -> None:
        """Test matching a sequence with a spread and single variable.

        Verifies that *A captures multiple elements and !B captures the last.
        """
        self.assertMatch(
            "Seq[*A !B]",
            "Seq[e f g]",
            {"A": ("e", "f"), "B": "g"},
        )

    def test_outer_term(self) -> None:
        """Test binding a variable to a nested term.

        Checks that a Var matches a Node and binds to the entire structure.
        """
        self.assertMatch(
            "!A",
            "abc[a b c]",
            {"A": Node("abc", ("a", "b", "c"))},
        )

    def test_splice_between_vars(self) -> None:
        """Test matching with spread variables between single variables.

        Ensures *A and *B capture sequences around a fixed element (x).
        """
        self.assertMatch(
            "Seq[*A x *B]",
            "Seq[a x c d]",
            {"A": ("a",), "B": ("c", "d")},
        )

    def test_splice_mismatch(self) -> None:
        """Test mismatching a sequence with incorrect fixed elements.

        Verifies that a Seq with a fixed 'x' fails to match a Seq with 'y'.
        """
        self.assertMatch("Seq[*A x *B]", "Seq[a y c d]", None)

    def test_multiple_splice_with_vars(self) -> None:
        """Test matching a sequence with multiple single and spread variables.

        Checks that !A, !B, *S, !C, !D correctly bind to a complex sequence.
        """
        self.assertMatch(
            "Seq[!A !B *S !C !D]",
            "Seq[a b s e q c d]",
            {
                "A": "a",
                "B": "b",
                "S": ("s", "e", "q"),
                "C": "c",
                "D": "d",
            },
        )

    def test_repeated_var(self) -> None:
        """Test matching a sequence with a repeated variable.

        Ensures that a repeated Var (!A) matches identical values.
        """
        self.assertMatch("Seq[!A !A]", "Seq[x x]", {"A": "x"})

    def test_var_guard(self) -> None:
        """Test matching variables with type guards.

        Verifies that guards (:int, :str, :X) enforce type or structure constraints.
        """
        self.assertMatch("!A:int", "a", None)  # String fails int guard
        self.assertMatch("!A:int", 1, dict(A=1))  # Integer passes int guard
        self.assertMatch("!A:str", 1, None)  # Integer fails str guard
        self.assertMatch("!A:str", "a", dict(A="a"))  # String passes str guard
        self.assertMatch("!A:X", node("Y", 123), None)  # Wrong node fails
        self.assertMatch("!A:X", node("X", 123), dict(A=node("X", 123)))


if __name__ == "__main__":
    unittest.main()
