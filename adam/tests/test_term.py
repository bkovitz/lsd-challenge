import unittest
from lsd.term import Node, Rule, Seq, Span, TermRule, Var, check_guard


class TestSeq(unittest.TestCase):
    def test_basic_seq(self):
        """Test basic Seq creation and string conversion"""
        s = Seq("a", "b")
        self.assertEqual(s, Seq("a", "b"))
        self.assertEqual(str(s), "Seq(a, b)")

    def test_seq_is_tuple(self):
        """Ensure Seq is a subclass of tuple and behaves as one"""
        s = Seq(1, 2, 3)
        self.assertIsInstance(s, tuple)
        self.assertIsInstance(s, Seq)
        self.assertEqual(s, (1, 2, 3))


class TestNode(unittest.TestCase):
    def test_basic_node(self):
        """Test basic Node creation and string representation"""
        n = Node("H", 1, 2)
        self.assertEqual(n.head, "H")
        self.assertEqual(n.body, Seq(1, 2))
        self.assertEqual(str(n), "H(1, 2)")

    def test_node_with_vars(self):
        """Test Node with variables as arguments"""
        x, y = Var("x"), Var("y")
        n = Node("add", x, y)
        self.assertEqual(n.head, "add")
        self.assertEqual(n.body, Seq(x, y))


class TestRule(unittest.TestCase):
    def test_basic_rule(self):
        """Test Rule construction and string representation"""
        r = TermRule("A", "B")
        self.assertEqual(r.pattern, "A")
        self.assertEqual(r.rhs, "B")

    def test_rule_with_terms(self):
        """Test Rule with Var and Node on left and right"""
        lhs = Var("x")
        rhs = Node("f", Var("y"))
        rule = TermRule(lhs, rhs)
        self.assertIsInstance(rule, Rule)
        self.assertEqual(rule.pattern, lhs)
        self.assertEqual(rule.rhs, rhs)


class TestVar(unittest.TestCase):
    def test_var_fields_and_repr(self):
        """Test Var fields and repr formatting"""
        v = Var.from_prefix("!", "x")
        self.assertEqual(v.name, "x")
        self.assertEqual(v.key, "!")

    def test_var_key_combinations(self):
        """Test all key variants of Var"""
        self.assertEqual(Var("x").key, "!")
        self.assertEqual(Var("x", Span(0, 1)).key, "?")
        self.assertEqual(Var("x", Span(1, None)).key, "+")
        self.assertEqual(Var("x", Span(0, None)).key, "*")


class TestGuard(unittest.TestCase):
    def test_check_guard(self):
        self.assertTrue(check_guard(str, "hi"))
        self.assertTrue(check_guard(int, 123))
        self.assertTrue(check_guard("Abc", Node("Abc")))
        self.assertTrue(check_guard(str, ("a", "b", "c")))
        self.assertTrue(check_guard(int, (1, 2, 3)))
        self.assertFalse(check_guard(int, "hi"))
        self.assertFalse(check_guard(int, ("a", "b", "c")))
        self.assertFalse(check_guard("Xyz", Node("Abc")))
