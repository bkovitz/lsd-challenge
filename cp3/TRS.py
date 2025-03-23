# trs.py -- Term-rewriting system for cp3

from __future__ import annotations
import re
from typing import Dict, List, Tuple, Union, Optional, Set, Any
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
    head: Symbol | Variable | SeqVariable | DollarSymbol
    args: Optional[Tuple[Term]] = None

    def __str__(self) -> str:
        if self.args:
            args_str = ' '.join(str(arg) for arg in self.args)
            return f'{self.head}[{args_str}]'
        else:
            return self.head

    def __repr__(self) -> str:
        if self.args:
            args_str = ', '.join(repr(arg) for arg in self.args)
            return f'Term({self.head!r}, [{args_str}])'
        else:
            return f'Term({self.head!r})'

Expr = Symbol | Term | Variable | SeqVariable

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

@dataclass(frozen=True)
class Subst:
    """A substitution: a function that maps variables to values."""
    d: PMap[Variable, Any] = field(default_factory=pmap)

    @classmethod
    def from_tups(cls, *tups: Tuple(str, Any)) -> Subst:
        term_tups = [
            (as_term(tup[0]), as_term(tup[1]))
                for tup in tups
        ]
        return cls(
            d=pmap(term_tups)
        )

    def eval(self, expr: Expr) -> Expr:
        match expr:
            case Symbol():
                return expr
            case Variable():
                try:
                    return self.d[expr]
                except KeyError:
                    raise UndefinedVariable(expr)
            case Term(head, args):
                return Term(head, tuple(self.eval(arg) for arg in args))
            case _:
                raise NotImplementedError

def pmatch(lhs: Term, rhs: Term) -> Subst:
    pass

@dataclass(frozen=True)
class RewritingSystem:
    rules: List[Rule]

    def __init__(self, rules_text: str):
        force_setattr(self, 'rules', list(parse_rules(rules_text)))

    def __str__(self) -> str:
        rules_str = '\n  '.join(str(rule) for rule in self.rules)
        return f'RewritingSystem(\n  {rules_str}\n)'

if __name__ == '__main__':
    #got = parse_rule('Stuff[arg1 $Succ[A] ARG2] -> Other[ARG2 xyz]')
    got = parse_rule('A -> x')
    print(got)

    su = Subst.from_tups(('A', 'x'))
    print(su)

