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

        # parse if str

        lhs = parse(pattern) if isinstance(pattern, str) else pattern
        rhs = parse(target) if isinstance(target, str) else target

        # convert to Env if dict
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
        self.assertEqual(pmatch(Symbol("x"), Symbol("x")), Env())
        self.assertIsNone(pmatch(Symbol("x"), Symbol("y")))

    def test_var_to_symbol(self) -> None:
        result = pmatch(Var("X"), "a")
        self.assertIsNotNone(result)
        assert result is not None  # Type hint for mypy
        self.assertEqual(result["X"], Symbol("a"))

    def test_nested_expr(self) -> None:
        pattern = Node("Wrap", (Var("A"),))
        target = Node("Wrap", (Symbol("v"),))
        result = pmatch(pattern, target)
        self.assertIsNotNone(result)
        assert result is not None  # Type hint for mypy
        self.assertEqual(result["A"], Symbol("v"))

    def test_complex_sequence(self) -> None:
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
        self.assertMatch("x", "x", {})

    def test_x_y(self) -> None:
        self.assertMatch("x", "y", None)

    def test_A_A(self) -> None:
        self.assertMatch("!A", "!A", {})

    def test_A_x(self) -> None:
        self.assertMatch("!A", "x", {"A": "x"})

    def test_seq_vars(self) -> None:
        self.assertMatch("Seq[!A !B]", "Seq[x y]", {"A": "x", "B": "y"})

    def test_A_A_x_x(self) -> None:
        self.assertMatch("Seq[!A !A]", "Seq[x x]", Env({"A": "x"}))

    def test_A_A_x_y(self) -> None:
        self.assertMatch("Seq[!A !A]", "Seq[x y]", None)

    def test_splice(self) -> None:
        self.assertMatch("Seq[*A]", "Seq[x y]", {"A": Seq(("x", "y"))})

    def test_splice_empty(self) -> None:
        self.assertMatch("Seq[*A]", "Seq[]", {"A": Seq()})

    def test_splice_with_var(self) -> None:
        self.assertMatch(
            "Seq[*A !B]",
            "Seq[e f g]",
            {"A": ("e", "f"), "B": "g"},
        )

    def test_outer_term(self) -> None:
        self.assertMatch(
            "!A",
            "abc[a b c]",
            {"A": Node("abc", ("a", "b", "c"))},
        )

    def test_splice_between_vars(self) -> None:
        self.assertMatch(
            "Seq[*A x *B]",
            "Seq[a x c d]",
            {"A": ("a",), "B": ("c", "d")},
        )

    def test_splice_mismatch(self) -> None:
        self.assertMatch("Seq[*A x *B]", "Seq[a y c d]", None)

    def test_multiple_splice_with_vars(self) -> None:
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
        self.assertMatch("Seq[!A !A]", "Seq[x x]", {"A": "x"})

    def test_var_guard(self):
        self.assertMatch("!A:int", "a", None)
        self.assertMatch("!A:int", 1, dict(A=1))
        self.assertMatch("!A:str", 1, None)
        self.assertMatch("!A:str", "a", dict(A="a"))
        self.assertMatch("!A:X", node("Y", 123), None)
        self.assertMatch("!A:X", node("X", 123), dict(A=node("X", 123)))


if __name__ == "__main__":
    unittest.main()
