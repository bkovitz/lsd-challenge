from __future__ import annotations

from .env import Env
from .term import Node, Seq, Term, Var


def substitute(term: Term, env: Env) -> Term:
    """
    Recursively substitute variables in a term with their bound values from the environment.
    """
    if isinstance(term, Var):
        return substitute_var(term, env)
    if isinstance(term, Seq):
        return substitute_seq(term, env)
    if isinstance(term, Node):
        return substitute_node(term, env)
    return term


def substitute_var(term: Var, env: Env) -> Term:
    """
    Substitute a variable using the environment.
    Assumes the bound value is a tuple of length 1.
    """

    if term.name not in env:
        raise KeyError(f"Var not found: {term.name}")

    value = env[term.name]

    if isinstance(value, tuple) and not isinstance(value, Seq):
        if len(value) == 1:
            return value[0]
        else:
            raise ValueError(f"Expected single value for variable {term.name}, got: {value}")

    return value


def substitute_node(term: Node, env: Env) -> Node:
    """
    Substitute a Node term by substituting its head and body.
    """

    new_head = substitute_var(term.head, env) if isinstance(term.head, Var) else term.head
    new_body = substitute(term.body, env)
    return Node(new_head, *new_body)


def substitute_seq(term: Seq, env: Env) -> Seq:
    """
    Substitute a sequence of terms.
    Variables are expanded if present; optional variables are skipped if unbound.
    """
    result = []
    for t in term:
        if isinstance(t, Var):
            if bound := env.get(t.name):
                result.extend(bound)
            elif t.is_optional:
                continue
            else:
                raise KeyError(f"Unbound variable: {t.name}")
        else:
            result.append(substitute(t, env))
    return Seq(*result)
