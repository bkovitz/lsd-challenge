import unittest
from parser import parse

from trs import TermRewriteSystem
from term import Node, Rule, Term, node


class TestRewriting(unittest.TestCase):

    def setUp(self) -> None:
        """Initialize a fresh TermRewriteSystem instance before each test."""
        self.trs = TermRewriteSystem()

    def assertRewrite(self, term: Term, expect: Term):
        """Custom assertion to check if rewriting a term yields the expected result."""
        self.assertEqual(self.trs.rewrite(term), expect)

    def test_with_vars(self) -> None:
        """Test rewriting a sequence with variables and a spread operator."""
        self.trs.add_rule("Seq[!A x *S] -> GotIt[*S !A]")
        self.assertRewrite(
            node("Seq", "a", "x", "b", "c"),
            node("GotIt", "b", "c", "a"),
        )

    def test_succ(self) -> None:
        """Test rewriting a simple Succ node (assuming no rules applied)."""
        self.assertRewrite(node("Succ", "a"), "b")

    def test_subexpression(self) -> None:
        """Test rewriting a sequence with a subexpression."""
        self.assertRewrite(
            parse("Seq[Succ[a] b c]"),
            parse("Seq[b b c]"),
        )

    def test_multistep(self) -> None:
        """Test multi-step rewriting with nested Succ applications."""
        self.assertRewrite(
            parse("Seq[a Succ[b] Succ[Succ[a]]]"),
            parse("Seq[a c c]"),
        )

    def test_no_match(self) -> None:
        """Test that a term with no matching rule remains unchanged."""
        self.assertRewrite(
            parse("Seq[x y]"),
            parse("Seq[x y]"),
        )

    def test_single_rule(self) -> None:
        """Test a single rule with a variable substitution."""
        self.trs.add_rule("Foo[!X] -> Bar[!X]")
        self.assertRewrite(
            parse("Foo[a]"),
            parse("Bar[a]"),
        )

    def test_nested_rewrite(self) -> None:
        """Test rewriting a nested sequence with multiple steps."""
        src = parse("Seq[a Succ[b] Succ[Succ[a]]]")
        target = parse("Seq[a c c]")
        self.assertRewrite(src, target)

    def test_recursive_vars(self) -> None:
        """Test rewriting with a spread variable in a recursive context."""
        self.trs.add_rule("Box[*A x] -> Wrap[*A]")
        term = parse("Box[a b c x]")
        self.assertRewrite(
            term,
            parse("Wrap[a b c]"),
        )

    @unittest.skip("infinite recursion")
    def test_multiple_splice_with_vars(self) -> None:
        """Test complex variable splicing (skipped due to infinite recursion)."""
        rule = Rule(
            parse("Seq[!A !B *S !C !D]"),
            parse("Seq[!C !D *S !A !B]"),
        )
        self.trs.add_rule(rule)
        self.assertRewrite(
            parse("Seq[a b s e q c d]"),
            parse("Seq[c d s e q a b]"),
        )

    def test_rule_front(self) -> None:
        """Test rewriting with a Front rule (assuming predefined method)."""
        self.assertRewrite(parse("Front[abc]"), "ab")

    def test_advance_last_rule(self) -> None:
        """Test rewriting with an AdvanceLast rule (assuming predefined method)."""
        self.assertRewrite(parse("AdvanceLast[abc]"), "abd")

    def test_new_world_rule(self) -> None:
        """Test rewriting with a NewWorld rule (assuming predefined method)."""
        self.assertRewrite(parse("NewWorld[abc Blank]"), node("NewWorld", "abd"))


if __name__ == "__main__":
    unittest.main()
