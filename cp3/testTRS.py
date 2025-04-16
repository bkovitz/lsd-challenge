import unittest

from TRS import RewritingSystem, parse_rule, as_term, Rule, Term, Variable, \
    DollarSymbol, Symbol, SeqVariable, pmatch, Subst, Splice, TermWithSeqBody

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

    # IDEA Don't make TermWithSeqBody. Just detect it in pmatch.
    def xtest_parse_term_with_seq_var(self) -> None:
        self.assertEqual(
            as_term('Seq[...A]'),
            TermWithSeqBody(Symbol('Seq'), (SeqVariable('...A')))
        )

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

    def test_pmatch_splice(self) -> None:
        self.assertEqual(
            pmatch(as_term('Seq[...A]'), as_term('Seq[x y]')),
            Subst.from_tups(('...A', Splice.from_text('x', 'y')))
        )

    def test_pmatch_splice_B(self) -> None:
        self.assertEqual(
            pmatch(as_term('Seq[...A B]'), as_term('Seq[e f g]')),
            Subst.from_tups(
                ('...A', Splice.from_text('e', 'f')),
                ('B', 'g')
            )
        )

    def test_pmatch_splice_a_x_c_d(self) -> None:
        self.assertEqual(
            pmatch(as_term('Seq[...A x ...B]'), as_term('Seq[a x c d]')),
            Subst.from_tups(
                ('...A', Splice.from_text('a')),
                ('...B', Splice.from_text('c', 'd'))
            )
        )

    def test_pmatch_splice_a_y_c_d(self) -> None:
        self.assertEqual(
            pmatch(as_term('Seq[...A x ...B]'), as_term('Seq[a y c d]')),
            Subst.bottom
        )

    def test_pmatch_splice_a_b_s_e_q_c_d(self) -> None:
        self.assertEqual(
            pmatch(as_term('Seq[A B ...S C D]'), as_term('Seq[a b s e q c d]')),
            Subst.from_tups(
                ('A', 'a'),
                ('B', 'b'),
                ('...S', Splice.from_text('s', 'e', 'q')),
                ('C', 'c'),
                ('D', 'd')
            )
        )

    def test_pmatch(self) -> None:
        self.assertEqual(
            pmatch(
                as_term('Seq[A A]'),
                as_term('Seq[x x]')
            ),
            Subst.from_tups(('A', 'x'))
        )

    def test_rewrite_succ(self) -> None:
        rules = '''
        Succ[a] -> b
        '''
        trs = RewritingSystem(rules)
        self.assertEqual(trs.reduce(as_term('Succ[a]')), as_term('b'))

    def test_rewrite_with_vars(self) -> None:
        rules = '''
        Succ[a] -> b
        Seq[A x ...S] -> GotIt[...S A]
        '''
        trs = RewritingSystem(rules)
        self.assertEqual(
            trs.reduce(as_term('Seq[a x b c]')),
            as_term('GotIt[b c a]')
        )
    
    def test_rewrite_subexpression(self) -> None:
        rules = '''
        Succ[a] -> b
        '''
        trs = RewritingSystem(rules)
        self.assertEqual(
            trs.reduce(as_term('Seq[Succ[a] b c]')),
            as_term('Seq[b b c]')
        )

    def test_rewrite_multistep(self) -> None:
        rules = '''
        Succ[a] -> b
        Succ[b] -> c
        '''
        trs = RewritingSystem(rules)
        self.assertEqual(
            trs.reduce(as_term('Seq[a Succ[b] Succ[Succ[a]]]')),
            as_term('Seq[a c c]')
        )
    def test_dollar_sign(self) -> None:
        rules = '''
        Succ[a] -> b
        Succ[b] -> c
        '''
        trs = RewritingSystem(rules)
        self.assertEqual(
            pmatch(
                as_term('Seq[A $Succ[A]]'),
                as_term('Seq[a b]'),
                trs
            ),
            Subst.from_tups(('A', 'a'))

        )

    def test_dollar_sign2(self) -> None:

        rules = '''
        Succ[a] -> b
        Succ[b] -> c
        '''
        trs = RewritingSystem(rules)
        self.assertEqual(
            pmatch(
                as_term('Seq[$Succ[A] A]'),
                as_term('Seq[b a]'),
                trs
            ),
            Subst.from_tups(('A', 'a'))

        )
