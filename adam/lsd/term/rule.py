from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from logging import getLogger
from typing import Any, Optional, Union

from .node import Node
from .term import Term, TermBase
from .var import Var

logger = getLogger(__name__)


class Rule(ABC, TermBase):
    """
    A rewrite rule: if lhs matches a term, produce rhs (or computed) result.
    """

    pattern: Term

    @abstractmethod
    def apply(self, term: Term) -> Optional[Term]:
        """Try to apply this rule to `term`. Return the rewritten Term or None."""
        ...

    @abstractmethod
    def name(self) -> str:
        """A human‑readable name for this rule."""
        ...

    def __repr__(self) -> str:
        return self.name()


@dataclass(frozen=True)
class TermRule(Rule, TermBase):
    """
    A direct pattern → replacement rule.
    """

    pattern: Term
    rhs: Term

    def name(self) -> str:
        return f"Rule({self.pattern} → {self.rhs})"

    def apply(self, term: Term) -> Optional[Term]:
        from lsd.match import match_pattern
        from lsd.method import Method
        from lsd.substitute import substitute

        env = match_pattern(self.pattern, term)
        if env is None:
            return None
        logger.debug("Applying %s to %r → %r", self.name(), term, self.rhs)
        return substitute(self.rhs, env)

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, TermRule) and other.pattern == self.pattern and other.rhs == self.rhs
        )
