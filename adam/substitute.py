from env import Env
from term import Node, Seq, Var, Term


def substitute(term: Term, env: Env) -> Term:
    """
    Substitute the variables in the term according to environment.
    Handles both single vars and variadic (*A) vars.
    """
    match term:
        case Var(name=name, many=many):
            if name not in env:
                raise KeyError(f"Var not found: {name}")
            return env[name] if many else env[name][0]

        case Node(head, body):
            new_head = substitute(head, env) if isinstance(head, Var) else head
            new_body = substitute(body, env)
            if not isinstance(new_body, Seq):
                raise ValueError()
            return Node(new_head, new_body)

        case Seq(items):
            return Seq(substitute(t, env) for t in items)

        case _:
            return term
