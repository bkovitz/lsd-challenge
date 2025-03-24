import unittest

from TRS import RewritingSystem, parse_rule, as_term, Rule, Term, Variable, \
    DollarSymbol, Symbol, SeqVariable, pmatch, Subst

class TestTRS(unittest.TestCase):
    
    maxDiff = None

    def test_parse_simple_rule(self) -> None:
        match parse_rule('A -> x'):
            case Rule(lhs, rhs):
                self.assertEqual(lhs, Variable('A'))
                self.assertEqual(rhs, Symbol('x'))
            case _:
                self.fail()

    def test_parse_rule(self) -> None:
        match parse_rule('Lhs[arg1 $Succ[A] ARG2] -> Rhs[ARG2 xyz]'):
            case Rule(lhs, rhs):
                match lhs:
                    case Term(head, body):
                        self.assertEqual(head, Symbol('Lhs'))
                        self.assertEqual(
                            body,
                            (
                                Symbol('arg1'),
                                Term(
                                    DollarSymbol('Succ'),
                                    (Variable('A'),)
                                ),
                                Variable('ARG2')
                            )
                        )
                    case _:
                        self.fail()
                match rhs:
                    case Term(head, body):
                        self.assertEqual(head, Symbol('Rhs'))
                        self.assertEqual(
                            body,
                            (
                                Variable('ARG2'),
                                Symbol('xyz')
                            )
                        )
                    case _:
                        self.fail()
            case _:
                self.fail()

    def test_as_term(self) -> None:
        self.assertEqual(
            as_term('Seq[A x]'),
            Term(Symbol('Seq'), (Variable('A'), Symbol('x')))
        )

    def test_subst(self) -> None:
        su = Subst.from_tups(('A', 'x'))
        self.assertEqual(
            su.eval(as_term('Seq[A]')),
            as_term('Seq[x]')
        )

    # TODO test exception when Subst fails?
    # TODO test ...V
    # TODO test $Succ[A]

    def test_pmatch_x_x(self) -> None:
        self.assertEqual(
            pmatch(as_term('x'), as_term('x')),
            Subst.empty
        )

    def test_pmatch_x_y(self) -> None:
        self.assertEqual(
            pmatch(as_term('x'), as_term('y')),
            Subst.bottom
        )

    def test_pmatch_A_A(self) -> None:
        self.assertEqual(
            pmatch(as_term('A'), as_term('A')),
            Subst.empty
        )
        
    def test_pmatch_A_x(self) -> None:
        self.assertEqual(
            pmatch(as_term('A'), as_term('x')),
            Subst.from_tups(('A', 'x'))
        )

    def test_pmatch_(self) -> None:
        self.assertEqual(
            pmatch(as_term('Seq[A B]'), as_term('Seq[x y]')),
            Subst.from_tups(('A', 'x'), ('B', 'y'))
        )

    def test_pmatch_A_A_x_x(self) -> None:
        self.assertEqual(
            pmatch(as_term('Seq[A A]'), as_term('Seq[x x]')),
            Subst.from_tups(('A', 'x'))
        )
        
    def test_pmatch_A_A_x_y(self) -> None:
        self.assertEqual(
            pmatch(as_term('Seq[A A]'), as_term('Seq[x y]')),
            Subst.bottom
        )

    """
    def test_pmatch(self) -> None:
        self.assertEqual(
            pmatch(
                as_term('Seq[A A]'),
                as_term('Seq[x x]')
            )
            Subst.from_tups(('A', 'x'))
        )

    def test_rewrite(self) -> None:
        rules = '''
        Succ[a] -> b
        '''
        trs = RewritingSystem(rules)
        print(trs)
    """
