from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, NamedTuple, Optional, Protocol, Type, Union

from .node import Node
from .seq import Seq
from .term import TermBase
from .types import Guard


class Span(NamedTuple):
    """
    Represents an inclusive range: [start, stop].
    If stop is None, the range is open-ended.

    >>> 999 in Span(0, None)
    True
    >>> list(Span(9, 11))
    [9, 10, 11]
    """

    start: int
    stop: int | None = 1

    def __contains__(self, x: Any) -> bool:
        return isinstance(x, int) and self.start <= x <= (self.stop or x)

    def __iter__(self):
        i = self.start
        stop = self.stop or 999_999
        while i <= stop:
            yield i
            i += 1


@dataclass(frozen=True)
class Var(TermBase):
    """
    Args:
    - name: The name of the variable; determines binding.
    - span: Determines how many values may be bound to variable.
            Default: Span(lo=1, hi=1) matches precisely one value.
    """

    name: str
    span: Span = field(default=Span(1, 1))
    guards: tuple[Guard, ...] = field(default=())

    @property
    def is_optional(self) -> bool:
        """Can this Var be None."""
        return self.span.start == 0

    @property
    def is_spread(self) -> bool:
        """Does this var potentially occupy multiple values."""
        return self.span.stop > 1 if self.span.stop else True

    @property
    def is_none(self) -> bool:
        """Must this Var be None."""
        return self.is_optional and self.span.stop == 0

    @property
    def key(self) -> str:
        """Returns the sigil representation: ?, !, *, +"""
        maybe = self.span.start == 0
        many = self.span.stop is None
        match maybe, many:
            case True, True:
                return "*"
            case True, False:
                return "?"
            case False, True:
                return "+"
            case False, False:
                return "!"
        raise ValueError(f"Invalid span for Var({self.name}): {self.span}")

    @classmethod
    def from_prefix(cls, key: str, name: str, guard: tuple[Guard, ...] = ()) -> Var:
        span = {
            "?": Span(0, 1),
            "!": Span(1, 1),
            "*": Span(0, None),
            "+": Span(1, None),
        }.get(key)
        if span is None:
            raise ValueError(f"Unknown sigil: {key}")
        return cls(name, span, tuple(guard))

    def __repr__(self) -> str:
        types = []
        for g in self.guards:
            if isinstance(g, str):
                types.append(g)
            else:
                types.append(g.__name__)
        types = ":" + ":".join(types) if self.guards else ""

        return f"Var.{self.key}{self.name}{types}"

    def check_span(self, value: tuple) -> bool:
        return len(value) in self.span

    def check_value(self, value):
        return any([check_guard(g, value) for g in self.guards])


def check_guard(guard: Guard, value) -> bool:
    if isinstance(value, (tuple, Seq)):
        return all(check_guard(guard, v) for v in value)
    elif isinstance(guard, str):
        return isinstance(value, Node) and value.head == guard
    else:
        return isinstance(value, guard)
