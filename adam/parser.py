from __future__ import annotations
from funs import split_at_depth
from term import Node, Rule, Seq, Symbol, Term, Var


class ParserError(Exception): ...


def parse(text: str) -> Term:
    VAR_KEYS = "! ? + *".split()

    text = text.strip()

    # Seq (new lines)
    if len(lines := split_at_depth(text, "\n")) > 1:
        return Seq(parse(line) for line in lines if line.strip())

    # Rule
    if "->" in text:
        parts = split_at_depth(text, "->")
        if len(parts) != 2:
            raise ValueError()
        return Rule(
            lhs=parse(parts[0]),
            rhs=parse(parts[1]),
        )

    # Seq (spaces)
    if len(lines := split_at_depth(text, sep=" ")) > 1:
        return Seq(parse(line) for line in lines if line.strip())

    # dollar sign
    if text[0] == "$":
        return Symbol(text)

    # variable
    if len(text) > 1 and text[0] in VAR_KEYS:
        name, *guard = text[1:].split(":")

        def map_guard(g: str):
            if g == "str":
                return str
            if g == "int":
                return int
            return g

        guard = tuple(map(map_guard, guard))
        match text[0]:
            case "!":
                return Var(name, none=False, many=False, guard=guard)
            case "?":
                return Var(name, none=True, many=False, guard=guard)
            case "+":
                return Var(name, none=False, many=True, guard=guard)
            case "*":
                return Var(name, none=True, many=True, guard=guard)

    # Expr like foo[bar baz] or f[]
    if "[" in text and text.endswith("]"):
        left = text.find("[")
        head = parse(text[:left])

        if not isinstance(head, (str, Var)):
            raise ParserError("head must be str or Var")

        body = tuple(
            parse(item)
            for item in split_at_depth(
                text[left + 1 : -1].strip(),
            )
        )

        return Node(head, body)

    # int
    if text.isdigit():
        return int(text)

    # Symbol
    if text.isalnum():
        return Symbol(text)

    raise ParserError(f"Invalid term: {text}")
