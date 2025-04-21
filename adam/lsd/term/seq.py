from __future__ import annotations

from typing import Any

from .term import Term, TermBase


class Seq(tuple, TermBase):
    """
    A symbolic sequence of terms.

    >>> Seq('a', 123)
    Seq(a, 123)
    """

    def __new__(cls, *values: Term):
        return tuple.__new__(Seq, values)

    def __repr__(self):
        return f"Seq({', '.join(map(str, self))})"

    def __eq__(self, other):
        return isinstance(other, (tuple, Seq)) and tuple(self) == tuple(other)

    def __hash__(self):
        return hash(tuple(self))

    def __len__(self):
        return tuple.__len__(self)

    def __getitem__(self, index):
        return tuple.__getitem__(self, index)

    @classmethod
    def ensure(cls, value: Any) -> Seq:
        if isinstance(value, Seq):
            return value
        if isinstance(value, tuple):
            return Seq(*value)
        return Seq(value)
