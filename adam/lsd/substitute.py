from __future__ import annotations

from .env import Env
from .logger import get_logger
from .term import Node, Rule, Seq, Term, TermBase, Var

logger = get_logger(__name__)


def substitute(term: Term, env: Env) -> Term:
    """
    Recursively substitute variables in a term with their bound values from the environment.
    """
    debug_substitute("substitute", term, env)
    if isinstance(term, Var):
        return substitute_var(term, env)
    if isinstance(term, Seq):
        return substitute_seq(term, env)
    if isinstance(term, Node):
        return substitute_node(term, env)
    return term


def debug_substitute(method_name: str, term: Term, env: Env) -> None:
    """Log a debug message for a substitution step."""
    logger.debug(f"{method_name:<24}{str(term):<16}{str(env):<16}")


def substitute_var(term: Var, env: Env) -> Term:
    """
    Substitute a variable using the environment.
    Assumes the bound value is a tuple of length 1.
    """
    debug_substitute("substitute_var", term, env)

    if term.name not in env:
        logger.error(f"Var not found in environment: {term.name}")
        raise KeyError(f"Var not found: {term.name}")

    value = env[term.name]

    if isinstance(value, tuple) and not isinstance(value, Seq):
        if len(value) == 1:
            return value[0]
        else:
            logger.error(f"Expected single value for variable {term.name}, got: {value}")
            raise ValueError(f"Expected single value for variable {term.name}, got: {value}")

    return value


def substitute_node(term: Node, env: Env) -> Node:
    """
    Substitute a Node term by substituting its head and body.
    """
    debug_substitute("substitute_node", term, env)

    new_head = substitute_var(term.head, env) if isinstance(term.head, Var) else term.head
    new_body = substitute(term.body, env)
    return Node(new_head, *new_body)


def substitute_seq(term: Seq, env: Env) -> Seq:
    """
    Substitute a sequence of terms.
    Variables are expanded if present; optional variables are skipped if unbound.
    """
    debug_substitute("substitute_seq", term, env)
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
