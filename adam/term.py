from __future__ import annotations

from dataclasses import dataclass, field
from typing import Type

Symbol = str
Seq = tuple

type Infinity = None
type Number = int | Infinity
type Atom = Symbol | Number
type Term = Atom | Var | Rule | Node | Seq
type Guard = str | Type


@dataclass(frozen=True)
class Var:
    name: Symbol
    none: bool = field(default=False)
    many: bool = field(default=False)
    guard: tuple[Guard, ...] = field(default_factory=tuple)

    def __repr__(self) -> str:
        return f"{self.name}"


@dataclass(frozen=True)
class Node:
    head: Term
    body: tuple[Term, ...] = ()

    def __eq__(self, other):
        return (
            isinstance(other, Node)
            and self.head == other.head
            and self.body == other.body
        )

    def __repr__(self):
        res = " ".join(map(str, self.body))
        return f"{self.head}[{res}]"


@dataclass(frozen=True)
class Rule:
    lhs: Term
    rhs: Term

    def __repr__(self) -> str:
        return f"{self.lhs} → {self.rhs}"

    def __iter__(self):
        yield self.lhs
        yield self.rhs


def seq(*body: Term) -> Seq:
    """
    >>> seq(1, 2, 3)
    (1, 2, 3)
    """
    return Seq(body)


def node(head: Term, *body: Term) -> Node:
    """
    >>> node("abc", 1, 2, 3)
    abc[1 2 3]
    """
    return Node(head, seq(*body))
