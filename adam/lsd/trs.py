from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from lsd.logger import get_logger
from lsd.method import Method, MethodRule, get_methods
from lsd.parser import parse_ensure
from lsd.rules import get_rules
from lsd.term import Node, Rule, Seq, Term, TermRule

logger = get_logger(__name__)


@dataclass(frozen=True)
class RewriteStep:
    rule: Rule
    input: Term
    output: Term
    cost: float = 1.0


class TermRewriteSystem:
    """
    Applies rewrite rules and methods to symbolic terms until a fixed point is reached,
    recording each fired step in self._trace.
    """

    _rules: list[Rule]
    trace: list[RewriteStep]

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        """
        Clear trace and reload:
         - all parser‑defined TermRules
         - a MethodRule for each built‑in Method
        """
        self.trace = []
        self._rules = get_rules()
        for m in get_methods():
            self._rules.append(MethodRule(m))

    def add_rule(
        self,
        first: Rule | Term | str,
        second: Optional[Term | str] = None,
    ) -> None:
        """
        Insert a new TermRule at highest priority.
        If `first` is already a Rule, we insert it directly.
        Otherwise parse `first` / `second` as LHS→RHS.
        """
        if isinstance(first, Rule):
            self._rules.insert(0, first)
        else:
            lhs = parse_ensure(first)
            if second is None:
                raise ValueError("Right-hand side required when adding a new rule.")
            rhs = parse_ensure(second)
            self._rules.insert(0, TermRule(lhs, rhs))

    def add_method(self, method: Method) -> None:
        """
        Wrap a Method into a MethodRule and insert at highest priority.
        """
        self._rules.insert(0, MethodRule(method))

    def rewrite(self, term: Term, max: int | None = None) -> Term:
        """
        Fully normalize `term` by repeatedly doing single‐step passes until no change.
        """
        out = self.rewrite_once(term)
        max = None if max is None else max - 1

        if max is None:
            return out if out == term else self.rewrite(out, max)
        else:
            while max > 0:
                term = self.rewrite_once(term)
                max -= 1
        return term

    def rewrite_once(self, term: Term) -> Term:
        # 1) Try every rule/method at the root
        for rule in self._rules:
            out = rule.apply(term)
            if out is not None:
                # record and return immediately
                self.trace.append(RewriteStep(rule, term, out, cost=1.0))
                return out

        # 2) If none fired, recurse into Node
        if isinstance(term, Node):
            new_args = [self.rewrite_once(arg) for arg in term.body]
            rebuilt = Node(term.head, *new_args)
            # try firing again on rebuilt node
            for rule in self._rules:
                out = rule.apply(rebuilt)
                if out is not None:
                    self.trace.append(RewriteStep(rule, rebuilt, out, cost=1.0))
                    return out
            return rebuilt

        # 3) Recurse into Seq
        if isinstance(term, Seq):
            items: list[Term] = []
            for elt in term:
                r = self.rewrite_once(elt)
                if isinstance(r, Seq):
                    items.extend(r)
                else:
                    items.append(r)
            rebuilt = Seq(*items)
            # try firing on rebuilt sequence
            for rule in self._rules:
                out = rule.apply(rebuilt)
                if out is not None:
                    self.trace.append(RewriteStep(rule, rebuilt, out, cost=1.0))
                    return out
            return rebuilt

        # 4) Atomic term with no rule applies
        return term

    def get_trace(self) -> list[RewriteStep]:
        """Return the list of RewriteSteps recorded since last reset."""
        return list(self.trace)

    def clear_trace(self) -> None:
        """Erase the recorded trace steps."""
        self.trace.clear()
