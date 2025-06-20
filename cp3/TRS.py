# trs.py -- Term-rewriting system for cp3

from __future__ import annotations
import re
from typing import Dict, List, Tuple, Union, Optional, Set, Any, Iterable
from dataclasses import dataclass, field

from lark import Lark, Transformer, v_args, Token
from pyrsistent import pmap
from pyrsistent.typing import PMap

from util import force_setattr, as_stripped_lines


@dataclass(frozen=True)
class Symbol:
    """An ordinary symbol, not a pattern variable. For example, Seq or x."""
    name: str

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name!r})'

@dataclass(frozen=True)
class Variable:
    name: str

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name!r})'

@dataclass(frozen=True)
class SeqVariable:
    """A variable that matches zero or more items in a row, indicated by an
    ellipsis at the beginning of the variable's name, e.g. ...A."""
    name: str

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name!r})'

@dataclass(frozen=True)
class DollarSymbol:
    """A symbol, preceded by a dollar sign, that serves as the head of a
    term that the corresponding item in a redex must reduce to. For example,
    $Succ[A]. Allowed only in an lhs."""
    name: str

    def __str__(self) -> str:
        return '$' + self.name

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name!r})'

@dataclass(frozen=True)
class Term:
    '''A Term is a symbol followed by brackets, which might contain
    arguments.'''
    head: Symbol | Variable | SeqVariable | DollarSymbol
    args: Optional[Tuple[Term, ...]] = None

    def __str__(self) -> str:
        if self.args:
            args_str = ' '.join(str(arg) for arg in self.args)
            return f'{self.head}[{args_str}]'
        else:
            return str(self.head)

    def __repr__(self) -> str:
        if self.args:
            args_str = ', '.join(repr(arg) for arg in self.args)
            return f'Term({self.head!r}, [{args_str}])'
        else:
            return f'Term({self.head!r})'

@dataclass(frozen=True)
class TermWithSeqBody:
    head: Symbol
    args: Tuple[Expr, ...]

    def __str__(self) -> str:
        if self.args:
            args_str = ' '.join(str(arg) for arg in self.args)
            return f'{self.head}[{args_str}]'
        else:
            return str(self.head)

    def __repr__(self) -> str:
        if self.args:
            args_str = ', '.join(repr(arg) for arg in self.args)
            return f'Term({self.head!r}, [{args_str}])'
        else:
            return f'Term({self.head!r})'

Expr = Symbol | Term | Variable | SeqVariable | TermWithSeqBody

@dataclass(frozen=True)
class Rule:
    lhs: Expr
    rhs: Expr

    def __str__(self) -> str:
        return f'{self.lhs} -> {self.rhs}'

grammar = r'''
?start: rule+

?rule: lhs_term "->" rhs_term           -> rule

?lhs_term: lhead
         | lhead "[" lhs_term* "]"      -> term_with_args

?lhead: SYMBOL                          -> symbol
      | ESYMBOL                         -> symbol
      | DSYMBOL                         -> symbol

?rhs_term: rhead                        
         | rhead "[" rhs_term* "]"      -> term_with_args

?rhead: SYMBOL                          -> symbol
      | ESYMBOL                         -> symbol

SYMBOL:  /[a-zA-Z][a-zA-Z0-9_-]*/
DSYMBOL: /\$[a-zA-Z][a-zA-Z0-9_-]*/
ESYMBOL: /\.\.\.[a-zA-Z][a-zA-Z0-9_-]*/

%import common.WS
%ignore WS
'''

@v_args(inline=True)
class Tr(Transformer):
    
    def symbol(self, x):
        return x

    def variable(self, token):
        return Variable(token)

    def symbol(self, token):
        if token[0] == '.':
            return SeqVariable(token)
        elif not any(char.islower() for char in token):
            return Variable(token)
        elif token[0] == '$':
            return DollarSymbol(token[1:])
            # BEN 22-Mar-2025 I think the DollarSymbol loses the metadata
            # from the token.
        else:
            return Symbol(token)

    def term_with_args(self, *tokens):
        return Term(tokens[0], tokens[1:])

    def rule(self, lhs, rhs):
        return Rule(lhs, rhs)

    def que(self, arg):
        return arg

parser = Lark(grammar, parser='lalr', transformer=Tr())
parse_rule = parser.parse

term_parser = Lark(grammar, parser='lalr', start='lhs_term', transformer=Tr())
as_term = term_parser.parse

def parse_rules(rules_text: str) -> Iterable[Rule]:
    for line in as_stripped_lines(rules_text):
        yield parse_rule(line)

########################################################################

class Fizzle(Exception):
    pass

class UndefinedVariable(Fizzle):
    pass

class SeqVariableAfterSeqVariable(Exception):
    pass

@dataclass(frozen=True)
class Splice:
    elems: Tuple[Expr, ...]

    @classmethod
    def from_text(cls, *args) -> Splice:
        return Splice(*(as_term(a) for a in args))

    def __init__(self, *elems: Expr):
        force_setattr(self, 'elems', tuple(elems))

    def __str__(self) -> str:
        elems_str = ' '.join(str(e) for e in self.elems)
        return f'Splice({elems_str})'

def as_value(x: str | Splice) -> Value:
    match x:
        case str():
            return as_term(x)
        case Splice():
            return x
        case _:
            return NotImplementedError

@dataclass(frozen=True)
class Subst:
    """A substitution: a function that maps variables to values."""
    d: PMap[Variable, Any] = field(default_factory=pmap)

    @classmethod
    def from_tups(cls, *tups: Tuple(str, Any)) -> Subst:
        term_tups = [
            #(as_term(tup[0]), as_term(tup[1]))
            (as_term(tup[0]), as_value(tup[1]))
                for tup in tups
        ]
        return cls(
            d=pmap(term_tups)
        )

    def is_bottom(self) -> bool:
        return False

    def __bool__(self) -> bool:
        """Not a bottom Subst, so true. No failure has occurred--even
        though the Subst might be empty."""
        return True

    def eval(self, expr: Expr) -> Expr:
        match expr:
            case Symbol():
                return expr
            case v if isinstance(v, (Variable, SeqVariable)):
                try:
                    return self.d[expr]
                except KeyError:
                    raise UndefinedVariable(expr)
            case Term(head, args):
                #return Term(head, tuple(self.eval(arg) for arg in args))
                result_args = []
                for arg in args:
                    y = self.eval(arg)
                    if isinstance(y, Splice):
                        result_args += list(y.elems)
                    else:
                        result_args.append(y)
                return Term(head, tuple(result_args))
            case _:
                raise NotImplementedError('eval', expr)

    # TODO rename rhs -> expr
    def pmatch(self, lhs: Term, rhs: Term, rules: Optional[RewritingSystem] = None) -> Subst:
        if lhs == rhs:
            return self
        match (lhs, rhs):
            case (var, _) if isinstance(var, (Variable, SeqVariable)):
                if lhs in self.d:
                    return self.pmatch(self.d[lhs], rhs, rules)
                else:
                    return Subst(self.d.set(lhs, rhs))
#            case (Term(DollarSymbol(dollar_name), dollar_args), _):
#                def resolve_dollar(su):
#                    t = su.eval(Term(Symbol(dollar_name), dollar_args))
#                    reduced = rules.reduce(t)
#                    return su.pmatch(reduced, rhs, rules)
#                return k(
            case (Term(left_head, left_args), Term(right_head, right_args)):
                result = self.pmatch(left_head, right_head, rules)
                return result.pmatch_seq(left_args, right_args, rules, False,
                    lambda su, new_rhs: su)
            #case (DollarSymbol(lhs_name), _):
                
                
            case _:
                return Subst.bottom

    def pmatch_seq(
        self,
        lhs: Iterable[Expr],
        rhs: Iterable[Expr],
        rules: Optional[RewritingSystem],
        after_seqvar: bool,
        k: Callable[[Subst, Iterable[Expr]], Subst]
    ) -> Subst:
        match lhs:
            case ():
                return k(self, rhs)
            case (t, *lhs_rest) \
            if isinstance(t, (Term, Symbol, Variable)) and not after_seqvar:
                # If Term or Variable, it must match first elem of rhs.
                match rhs:
                    case (x, *rhs_rest):
                        return self.pmatch(t, x, rules) \
                                   .pmatch_seq(lhs_rest, rhs_rest, rules, False, k)
                    case ():
                        return Subst.bottom
            case (SeqVariable() as seqvar, *lhs_rest):
                # If ...α, set after_seqvar and slurp up the entire rhs
                # in the continuation.
                if after_seqvar:
                    raise SeqVariableAfterSeqVariable  # not allowed
                def pmatch_seqvar_to_whole_new_rhs(su, new_rhs):
                    return k(su.pmatch(seqvar, Splice(*new_rhs), rules), ())
                return self.pmatch_seq(lhs_rest, rhs, rules, True,
                    pmatch_seqvar_to_whole_new_rhs)
            case (t, *lhs_rest) \
            if isinstance(t, (Term, Symbol)) and after_seqvar:
                # If ...α followed by Term: search ahead to match Term.
                su, rhs_pre_term, rhs_post_term = \
                    self.find_pmatch_in_seq(t, rhs, rules)
                def continue_on_previous_rhs_segment(su, new_rhs):
                    return k(su, rhs_pre_term)
                return su.pmatch_seq(lhs_rest, rhs_post_term, rules, False,
                    continue_on_previous_rhs_segment)
            case (Variable() as var, *lhs_rest) if after_seqvar:
                # If ...α followed by Variable: wait until the end and then
                # match the last elem to the Variable.
                def pmatch_var_to_last_elem(su, new_rhs):
                    result = k(su.pmatch(var, new_rhs[-1]), new_rhs[:-1])
                    return result
                return self.pmatch_seq(lhs_rest, rhs, rules, True,
                    pmatch_var_to_last_elem)
            case _:
                raise NotImplementedError(
                    'pmatch_seq', lhs, rhs, rules, after_seqvar, k
                )

    def find_pmatch_in_seq(self, term: Term, seq: Iterable[Expr], rules: Optional[RewritingSystem] = None) \
    -> Tuple[Subst, Iterable[Expr], Iterable[Expr]]:
        for i, elem in enumerate(seq):
            if not (su := self.pmatch(term, elem, rules)).is_bottom():
                return su, seq[:i], seq[i+1:]
        return Subst.bottom, (), ()

    def __str__(self) -> str:
        pmap_str = ', '.join(f'{k} ↦ {v}' for k, v in self.d.items())
        return f'Subst({pmap_str})'

class BottomSubst(Subst):

    def is_bottom(self) -> bool:
        return True

    def __bool__(self) -> bool:
        return False

    def eval(self, expr: Expr) -> Expr:
        # TODO What should eval on a bottom return?
        raise NotImplementedError

    def pmatch(self, lhs: Term, rhs: Term, rules: Optional[RewritingSystem] = None) -> Subst:
        return self

    def pmatch_seq(
        self,
        lhs: Iterable[Expr],
        rhs: Iterable[Expr],
        rules: Optional[RewritingSystem],
        after_seqvar: bool,
        k: Callable[[Subst, Iterable[Expr]], Subst]
    ) -> Subst:
        return self

    def __str__(self) -> str:
        return 'BottomSubst'

    __repr__ = __str__

Subst.empty = Subst(pmap())
Subst.bottom = BottomSubst()


def pmatch(lhs: Term, rhs: Term, rules: Optional[RewritingSystem] = None) \
-> Subst:
    return Subst.empty.pmatch(lhs, rhs, rules)

@dataclass(frozen=True)
class RewritingSystem:
    rules: List[Rule]

    def __init__(self, rules_text: str):
        force_setattr(self, 'rules', list(parse_rules(rules_text)))

    def reduce(self, e: Expr) -> Expr:
        for rule in self.rules:
            # match rule.lhs:
            #     case Term(head, args):
            #         for arg in args:
            #         if pmatch(rule.lhs, head):
            if (su := pmatch(rule.lhs, e, self)):
                return su.eval(rule.rhs)
        match e:
            case Term(head, args):
                reduced_args = tuple(self.reduce(arg) for arg in args)
                if reduced_args != args:
                    return self.reduce(Term(head, reduced_args))
        return e

    def __str__(self) -> str:
        rules_str = '\n  '.join(str(rule) for rule in self.rules)
        return f'RewritingSystem(\n  {rules_str}\n)'

if __name__ == '__main__':
    #got = parse_rule('Stuff[arg1 $Succ[A] ARG2] -> Other[ARG2 xyz]')
    got = parse_rule('A -> x')
    print(got)

    got = parse_rule('Seq[...A] -> Blah[...A]')
    print(got)

    got = pmatch(as_term('Seq[...A]'), as_term('Seq[x]'))
    print(got)

    #su = Subst.from_tups(('A', 'x'))
    #print(su)
