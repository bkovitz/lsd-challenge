from copy import deepcopy
from typing import Optional

from env import Env
from term import Node, Seq, Symbol, Term, Var


def pmatch(
    pattern: Term,
    template: Term,
    env: Env | None = None,
) -> Env | None:
    """Pattern-match a pattern term against a template term, updating the environment."""

    if env is None:
        env = Env()

    if pattern == template:
        return env

    match pattern, template:
        case Var(), _:
            return pmatch_var(pattern, template, env)

        case Seq(), Seq():
            return pmatch_seqs(pattern, template, env)

        case Node(p_head, p_body), Node(t_head, t_body):
            head_env = pmatch(p_head, t_head, env)
            body_env = pmatch(p_body, t_body, env)
            return Env.combine(head_env, body_env)
    return None


def pmatch_seqs(
    pattern: Seq,
    template: Seq,
    env: Env,
) -> Env | None:
    """Match one sequence to another."""

    def try_match(p_rest, t_rest, e):
        """Try various sizes of Var to fit Seq"""
        if not p_rest and not t_rest:
            return e
        if not p_rest:
            return None
        if not t_rest:
            for pr in p_rest:
                if not (isinstance(pr, Var) and pr.many and pr.none):
                    return None
                name = pr.name
                if name in e:
                    if e[name] != Seq(()):
                        return None
                else:
                    e[name] = Seq(())
            return e

        head = p_rest[0]

        # Spread match
        if isinstance(head, Var) and head.many:
            name = head.name

            min_len = 0 if head.none else 1
            max_len = len(t_rest) - (len(p_rest) - 1)
            for i in range(min_len, max_len + 1):
                slice_val = t_rest[:i]
                rest_t = t_rest[i:]

                new_env = deepcopy(e)

                if name in new_env:
                    if new_env[name] != Seq(slice_val):
                        continue
                else:
                    new_env[name] = Seq(slice_val)

                result = try_match(p_rest[1:], rest_t, new_env)
                if result is not None:
                    return result

            return None
        else:
            matched = pmatch(head, t_rest[0], deepcopy(e))
            if matched is None:
                return None
            return try_match(p_rest[1:], t_rest[1:], matched)

    return try_match(list(pattern), list(template), Env(env))


def pmatch_var(pattern: Var, template: Term, env: Env) -> Env | None:
    """Match Var to a term."""
    if pattern.name in env:
        # If variable is already bound, check consistency
        return env if env[pattern.name] == template else None

    else:
        # Bind the variable to the template
        # Use Seq for 'many', else direct binding
        for g in pattern.guard:
            if g == str:
                if not isinstance(template, str):
                    return None
            elif g == int:
                if not isinstance(template, int):
                    return None
            elif not isinstance(template, Node):
                return None
            elif template.head != g:
                return None

        print("guard", pattern.guard, "template", template)
        env[pattern.name] = Seq((template,)) if pattern.many else template
        return env
