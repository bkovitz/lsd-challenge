# l.py -- Playing around with Lark in order to learn it

from __future__ import annotations
import re
from typing import Dict, List, Tuple, Union, Optional, Set, Any
from dataclasses import dataclass

from lark import Lark, Transformer, v_args, Token


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
    args: Optional[List[Term]] = None

    def __str__(self) -> str:
        if self.args:
            args_str = ' '.join(str(arg) for arg in self.args)
            return f'{self.head}[{args_str}]'
        else:
            return self.head

    def __repr__(self) -> str:
        if self.args:
            args_str = ', '.join(repr(arg) for arg in self.args)
            return f'Term({self.head}, [{args_str}])'
        else:
            return f'Term({self.head})'

@dataclass(frozen=True)
class Rule:
    lhs: Term | Variable | SeqVariable
    rhs: Term | Variable | SeqVariable

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
    
    def got(self, *args, **kwargs):
        print(args, kwargs)
        match args[0]:
            case Token('SYMBOL', name):
                return Term(name, args[1:])
            case _:
                print("HERE")
    
    def symbol(self, x):
        print("x:", x)
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
        print('tokens:', repr(tokens))
        return Term(tokens[0], tokens[1:])

    def rule(self, lhs, rhs):
        return Rule(lhs, rhs)

    def que(self, arg):
        print('que:', arg)
        return arg

parser = Lark(grammar, parser='lalr', transformer=Tr())
got = parser.parse('Stuff[arg1 $Succ[A] ARG2] -> Other[ARG2 xyz]')
print(got)
