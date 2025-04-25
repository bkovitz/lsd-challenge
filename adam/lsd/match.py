from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional

from .env import Env
from .term import Node, Seq, Term, Var, Wildcard


def match_pattern(
    pattern: Term | Any,
    target: Term | Any,
    env: Env | None = None,
) -> Env | None:
    """
    Try to match `pattern` against `target`, threading through `env`.
    Returns a fresh Env on success, or None on failure.
    """
    env = deepcopy(env) if env is not None else Env()

    # 1) Literal equality
    if pattern == target:
        return env

    # 2) Wildcard matches anything (does not bind to the environment)
    if isinstance(pattern, Wildcard):
        if isinstance(target, Seq):
            return _match_seq(Seq(pattern), target, env)
        return env

    # 3) Variable matching
    if isinstance(pattern, Var):
        return _match_var(pattern, target, env)

    # 4) Sequence matching
    if isinstance(pattern, Seq) and isinstance(target, Seq):
        return _match_seq(pattern, target, env)

    # 5) Node matching
    if isinstance(pattern, Node) and isinstance(target, Node):
        env2 = match_pattern(pattern.head, target.head, env)
        if env2 is None:
            return None
        if env3 := match_pattern(pattern.body, target.body, env2):
            return env3

    # No match found
    return None


def _match_var(
    pattern: Var,
    target: Any,
    env: Env,
) -> Optional[Env]:
    """
    Handle matching for variable patterns (e.g., !X, ?X, *X, +X), considering guards and spans.

    Args:
        pattern (Var): The variable pattern to match.
        target (Any): The target to match the variable against.
        env (Env): The current environment holding variable bindings.

    Returns:
        Optional[Env]: The updated environment if successful, or None if matching fails.
    """

    # 1) Guard check: ensure the value meets the variable's guard conditions
    if pattern.guards and not pattern.check_value(target):
        return env.bind(pattern.name, ()) if pattern.is_optional else None

    # 2) Plain tuple binding for variables (whether spread or not)
    value = (
        (target,)
        if not pattern.is_spread
        else tuple(target) if isinstance(target, Seq) else (target,)
    )

    # 3) Span check (e.g., *X requires at least one element, +X requires >=1)
    if not pattern.check_span(value):
        return None

    # 4) Bind the variable, checking for consistency if already bound
    prev = env.get(pattern.name)
    if prev is None:
        return env.bind(pattern.name, value)
    return env if prev == value else None


def _match_seq(
    p_seq: Seq,
    t_seq: Seq,
    env: Env,
) -> Optional[Env]:
    """
    Match sequence patterns, handling both fixed and spread variables, including wildcards.

    Args:
        p_seq (Seq): The pattern sequence to match.
        t_seq (Seq): The target sequence to match against.
        env (Env): The current environment holding variable bindings.

    Returns:
        Optional[Env]: The updated environment if the match is successful, or None if matching fails.
    """
    p_elems = list(p_seq)
    t_elems = list(t_seq)

    # Both sequences empty -> match successful
    if not p_elems and not t_elems:
        return env

    # Pattern is empty, but target has remaining elements -> fail
    if not p_elems:
        return None

    # Target is empty, pattern must consist of optional vars
    if not t_elems:
        e2 = deepcopy(env)
        for pe in p_elems:
            if not (isinstance(pe, Var) and pe.is_optional):
                return None
            e2[pe.name] = ()
        return e2

    first, *rest = p_elems

    # 2) Spread variable at the front: try all possible splits
    if isinstance(first, Var) and first.is_spread:
        for cut in range(len(t_elems) - len(rest) + 1):
            candidate = tuple(t_elems[:cut])
            e2 = deepcopy(env)
            prev = e2.get(first.name)
            if prev is not None and prev != candidate:
                continue
            e2[first.name] = candidate
            res = _match_seq(Seq(*rest), Seq(*t_elems[cut:]), e2)
            if res is not None:
                return res
        return None

    # 3) Non-spread variable: match head and recurse on the rest
    env2 = match_pattern(first, t_elems[0], deepcopy(env))
    if env2 is None:
        return None
    return _match_seq(Seq(*rest), Seq(*t_elems[1:]), env2)
