"""
Term Rewriting System
"""

from __future__ import annotations
from dataclasses import dataclass, field


class Expr:
    head: str
    children: list[Expr]

    def __init__(self, head, *sub_exprs):
        self.head = head
        self.children = list(sub_exprs)

    @classmethod
    def parse(cls, text: str) -> Expr:
        open_bracket = text.find("[")

        if open_bracket == -1:
            return Expr(text)

        return Expr(text[:open_bracket], text[open_bracket:])

    def __str__(self):
        if not self.children:
            return self.head
        children = ", ".join([str(c) for c in self.children])

        return self.head + children

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, Expr):
            return False
        if self.head != other.head:
            return False
        for lchild in self.children:
            if lchild not in other.children:
                return False
        for rchild in other.children:
            if rchild not in self.children:
                return False
        return True


@dataclass
class TRS:
    rules: list[tuple[Expr, Expr]] = field(default_factory=list)

    def add_rule(self, lexpr: Expr, rexpr: Expr) -> None:
        self.rules.append((lexpr, rexpr))

    def reduce(self, expr: Expr) -> Expr:
        """Apply rules to expression"""
        for rule in self.rules:
            if expr == rule[0]:
                return rule[1]
        return expr


# Testing


from typing import Type
import unittest


class TestTRS(unittest.TestCase):
    def test_parse(self):
        a = Expr.parse("Chunk[Run]")
        b = Expr.parse("Chunk[Run[Length[3]]]")
        self.assertEqual(a, Expr("Chunk", Expr("Run")))
        self.assertEqual(b, Expr("Chunk", Expr("Run", Expr("Length", 3))))

    def test_rewrite(self):
        trs = TRS()
        a = Expr.parse("Chunk[Run[Length[3]]]")
        b = Expr.parse("Chunk[Run]")
        trs.add_rule(a, b)
        print(a, b)
        self.assertEqual(trs.reduce(a), b)

    def test_delta(self):
        ...

        # self.assertEqual(trs.delta(a, b), (a, b))
        # self.assertEqual(trs.delta(a, b), (a, b))


## From TRS class:
#
# def delta(self, left_expr: Expr, right_expr: Expr) -> tuple:
#     if left_expr.head != right_expr.head:
#         return (left_expr, right_expr)

#     left_children = []
#     right_children = []

#     for c in left_expr.children:
#         if c not in right_expr.children:
#             left_children.append(c)
#     for c in right_expr.children:
#         if c not in left_expr.children:
#             right_children.append(c)

#     return (
#         Expr(left_expr.head, *left_children),
#         Expr(right_expr.head, *right_children),
#     )
