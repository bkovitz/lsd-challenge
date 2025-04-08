from __future__ import annotations

from dataclasses import dataclass, field
from parser import parse

from env import Env
from rules import get_rules
from method import Method, get_methods
from pmatch import pmatch
from substitute import substitute
from term import Node, Rule, Seq, Term, Var, node


@dataclass
class TermRewriteSystem:
    rules: Env = field(default_factory=Env)
    methods: dict[str, Method] = field(default_factory=dict)

    def __post_init__(self):
        self.methods.update(get_methods())
        self.rules.update(get_rules())

    def add_rule(self, rule) -> None:
        match rule:
            case Rule(lhs, rhs):
                self.rules[lhs] = rhs
            case list(rules):
                for rule in rules:
                    self.add_rule(rule)
            case str(text):
                self.add_rule(parse(text))
            case _:
                raise Exception()

    def rewrite(self, term: Term, /, max_steps: int = 10) -> Term:
        if isinstance(term, Seq):
            return Seq(self.rewrite(t) for t in term)
        current = term
        for _ in range(max_steps):
            next_term = self.rewrite_step(current)
            if next_term == current:
                return current
            current = next_term
        return current

    def rewrite_step(self, term: Term, steps_left: int = 10) -> Term:
        if steps_left <= 0:
            return term

        for pattern, replacement in self.rules.items():
            bindings = pmatch(pattern, term)
            if bindings is not None:
                print("binding", bindings)
                result = substitute(replacement, bindings)
                return self.rewrite_step(result, steps_left - 1)

        if isinstance(term, Node):
            rewritten_body = tuple(
                self.rewrite_step(arg, steps_left - 1) for arg in term.body
            )
            # splice value if sequence
            res = []
            for t in rewritten_body:
                rw = self.rewrite(t)
                if isinstance(rw, Seq):
                    res = [*res, *rw]
                else:
                    res.append(rw)
            rewritten_body = Seq(res)

            # check if node is a method
            if method := self.methods.get(str(term.head)):
                try:
                    if len(rewritten_body) == len(method.guards):
                        result = method(*rewritten_body)
                        return self.rewrite_step(result, steps_left - 1)
                except (TypeError, ValueError):
                    pass
            return Node(term.head, rewritten_body)

        return term
