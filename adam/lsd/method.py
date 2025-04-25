from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional

from .term import Node, Rule, Term, TermBase, Var
from .util import check


@dataclass(frozen=True)
class Method:
    """
    A named transformation on terms that can be applied to arguments.

    Attributes:
        name (str): The name of the method.
        exec (Callable[..., Any]): The function that performs the transformation.
        cond (Callable[..., bool]): A condition that must be met for the method to apply (defaults to always True).
    """

    name: str
    exec: Callable[..., Any]
    cond: Callable[..., bool] = check.is_any  # Default condition is always true

    def __call__(self, arg: Any) -> TermBase | None:
        """
        Apply the method to a given argument.

        Args:
            arg (Any): The argument to apply the method to.

        Returns:
            TermBase | None: The result of the transformation, or None if the condition fails.
        """
        if not self.cond(arg):
            return None
        return self.exec(arg)

    @classmethod
    def compose(cls, *methods: Method) -> Method:
        """
        Compose multiple methods into a single method.

        Args:
            *methods (Method): The methods to compose.

        Returns:
            Method: A new method that applies the composed functions.
        """
        name = ".".join(m.name for m in methods)

        def exec(x):
            val = x
            for m in methods:
                val = m(val)
            return val

        return Method(name=name, exec=exec)

    def repeat(self, n: int) -> Method:
        """
        Repeat the method `n` times.

        Args:
            n (int): The number of times to repeat the method.

        Returns:
            Method: A new method that applies the original method `n` times.
        """
        if n < 1:
            raise ValueError("repeat count must be ≥1")
        return Method.compose(*([self] * n))


class MethodRule(Rule):
    """
    A rule that applies a method on a single captured argument.

    The LHS of the rule is `MethodName(X)`, where `X` is a variable. The RHS is the result of invoking the method's `exec` function on `X`.
    """

    def __init__(self, method: "Method"):
        """
        Initializes the MethodRule.

        Args:
            method (Method): The method to apply when the rule is matched.
        """
        self.method = method
        self.var = Var("X")  # A variable to capture the argument for the method
        self.pattern = Node(method.name, self.var)

    def name(self) -> str:
        """Return a string representing the name of the rule."""
        return f"MethodRule({self.method.name})"

    def apply(self, term: Term) -> Optional[Term]:
        """
        Apply the method to the matched term.

        Args:
            term (Term): The term to apply the rule to.

        Returns:
            Optional[Term]: The result of applying the method, or None if no match is found.
        """
        from lsd.match import match_pattern

        # Match the term against the pattern
        env = match_pattern(self.pattern, term)
        if env is None:
            return None

        # Get the value for the method's argument
        vals = env[self.var.name]
        arg = vals[0] if len(vals) == 1 else tuple(vals)

        # Try to apply the method
        try:
            result = self.method(arg)
            return result
        except RuntimeError as e:
            return None

    def __eq__(self, other: Any) -> bool:
        """Check equality between two MethodRule objects."""
        return isinstance(other, MethodRule) and other.method.name == self.method.name


# Core Methods (no guards parameter; use cond for predicates)

# Define various core methods like Pred, Succ, Max, Min, etc.
Pred = Method(
    name="Pred",
    exec=lambda x: chr(ord(x) - 1),
    cond=check.is_char,
)

Succ = Method(
    name="Succ",
    exec=lambda x: chr(ord(x) + 1),
    cond=check.is_char,
)

Max = Method(
    name="max",
    exec=lambda *xs: max(*xs),
    cond=check.is_iter,
)

Min = Method(
    name="min",
    exec=lambda *xs: min(*xs),
    cond=check.is_iter,
)

Identity = Method(
    name="identity",
    exec=lambda s: s,
    cond=check.is_any,
)

Reverse = Method(
    name="reverse",
    exec=lambda s: s[::-1],
    cond=check.is_any,
)

RotateRight1 = Method(
    name="rotate_right_1",
    exec=lambda s: s[-1] + s[:-1],
    cond=lambda _: True,
)

SwapFirstLast = Method(
    name="swap_first_last",
    exec=lambda s: s[-1] + s[1:-1] + s[0] if len(s) > 1 else s,
    cond=lambda _: True,
)

# Composed Methods

Rotate2ThenReverse = Method.compose(RotateRight1, RotateRight1, Reverse)
TripleSucc = Succ.repeat(3)

# Registry of Methods (can be expanded later)
_METHODS = [
    Pred,
    Succ,
    Max,
    Min,
    Identity,
    Reverse,
    RotateRight1,
    SwapFirstLast,
]


def get_methods() -> list[Method]:
    """Return the list of available methods."""
    return list(_METHODS)
