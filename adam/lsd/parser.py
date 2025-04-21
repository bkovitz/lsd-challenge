from __future__ import annotations

from lsd.term import Guard, Node, Rule, Seq, Term, TermRule, Var
from lsd.term.var import Span
from lsd.term.wildcard import Wildcard
from lsd.util.string import is_balanced, isfloat, split_at_depth


class ParserError(ValueError):
    """Custom error for parsing-related issues."""

    pass


def parse(text: str) -> Term:
    """
    Parse a given string into a corresponding `Term` object.

    The function identifies different term types (e.g., sequences, nodes, variables, etc.)
    and returns the appropriate term.

    Args:
        text (str): The input string to parse.

    Returns:
        Term: The parsed term (could be a `Node`, `Seq`, `Var`, etc.).

    Raises:
        ValueError: If the text cannot be parsed into a valid term.
    """
    text = text.strip()

    # Parse rule if the text contains a top-level "->"
    if "->" in text:
        parts = split_at_depth(text, "->")
        if len(parts) > 1:
            return parse_rule(text)

    # Parse sequence (spaces or new lines)
    if len(split_at_depth(text, sep=" ")) > 1 or len(split_at_depth(text, "\n")) > 1:
        return parse_seq(text)

    # Parse parenthesized terms (e.g., (A -> B))
    if text.startswith("(") and text.endswith(")"):
        if is_balanced(text):
            return parse(text[1:-1].strip())

    # Return empty sequence for empty input
    if len(text) == 0:
        return Seq()

    if text[0] == "_":
        return Wildcard()

    # Parse dollar sign as a symbol
    if text[0] == "$":
        return str(text)

    # Parse variable (starting with !, ?, +, or *)
    if text[0] in "!?+*":
        return parse_var(text)

    # Parse node if it looks like a list [A, B, C]
    if "[" in text and text.endswith("]"):
        return parse_node(text)

    # Parse integer, float, or symbol
    if text.isdigit():
        return int(text)
    if isfloat(text):
        return float(text)
    if text.isalnum():
        return str(text)

    # If no valid pattern matched, raise an error
    raise ValueError(f"Could not parse: {text}")


def parse_seq(text: str, sep: str = " ") -> Seq:
    """
    Parse a sequence of terms separated by the specified separator.

    Args:
        text (str): The input string to parse.
        sep (str): The separator for splitting the sequence (default is space).

    Returns:
        Seq: A sequence of parsed terms.
    """
    texts = split_at_depth(text, sep)
    return Seq(*[parse(t) for t in texts])


def parse_ensure(term: Term | str) -> Term:
    """
    Ensure that the input is a parsed `Term`. If the input is a string, it will be parsed.

    Args:
        term (Term | str): The term to ensure (either a string to parse or a Term object).

    Returns:
        Term: The parsed term, or the original `Term` if it was already a `Term`.
    """
    return parse(term) if isinstance(term, str) else term


def parse_rule_sides(left: str, right: str) -> Rule:
    """
    Parse the left-hand side and right-hand side of a rule.

    Args:
        left (str): The left-hand side of the rule (string).
        right (str): The right-hand side of the rule (string).

    Returns:
        Rule: A `TermRule` object representing the parsed rule.
    """
    return TermRule(parse(left), parse(right))


def parse_rule(text: str) -> Rule:
    """
    Parse a string representing a rule, where the rule is defined as `LHS -> RHS`.

    Args:
        text (str): The rule string to parse.

    Returns:
        Rule: A `TermRule` representing the parsed rule.

    Raises:
        ParserError: If the rule format is invalid.
    """
    *rest, l, r = map(parse, split_at_depth(text, "->"))
    acc = TermRule(l, r)
    for part in rest[::-1]:
        acc = TermRule(part, acc)
    return acc


def parse_var(text: str) -> Var:
    """
    Parse a variable, handling different prefixes (e.g., !X, ?X, *X) and guards.

    Args:
        text (str): The variable string to parse.

    Returns:
        Var: A `Var` object representing the parsed variable.

    Raises:
        AssertionError: If the variable string format is incorrect.
    """
    assert len(text) > 1  # Variable name must be at least 2 characters (prefix + name)

    prefix = text[0]
    name, *guard = text[1:].split(":")

    VAR_SPAN = {
        "!": Span(1, 1),
        "?": Span(0, 1),
        "*": Span(0, None),
        "+": Span(1, None),
    }

    assert prefix in VAR_SPAN  # Ensure the variable has a valid prefix

    span = VAR_SPAN[prefix]

    # Parse guards (e.g., int, str, etc.)
    guard = tuple(map(parse_guard, guard))
    return Var(name, span, guard)


def parse_guard(g: str) -> Guard:
    """
    Parse a guard, which specifies a type constraint for a variable.

    Args:
        g (str): The guard string (e.g., "int", "str").

    Returns:
        Guard: The parsed guard (either a type or a string).
    """
    return {"int": int, "str": str, "float": float, "bool": bool}.get(g, g)


def parse_node(text: str) -> Node:
    """
    Parse a node, which is a term that contains a head and a body (e.g., Node(A, B)).

    Args:
        text (str): The node string to parse.

    Returns:
        Node: A `Node` object representing the parsed node.

    Raises:
        AssertionError: If the node format is incorrect.
    """
    left = text.find("[")
    assert left > 0 and "]" == text[-1]  # Ensure the node format is correct

    head = parse(text[:left])

    body = (
        parse(item)
        for item in split_at_depth(
            text[left + 1 : -1].strip(),
        )
    )
    return Node(head, *body)
