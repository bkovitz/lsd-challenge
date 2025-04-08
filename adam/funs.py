from term import Node, Rule, Term, Var


def split_at_depth(s: str, sep: str = " ") -> list[str]:
    """
    Splits a string by separator (not between brackets). Useful for parsing.
    >>> split_at_depth('[a b] [c d]')
    ['[a b]', '[c d]']
    """
    parts = []
    depth = 0
    buf = []
    i = 0
    while i < len(s):
        char = s[i]

        if char == "[":
            depth += 1
            buf.append(char)
            i += 1
            continue
        elif char == "]":
            depth -= 1
            buf.append(char)
            i += 1
            continue

        if depth == 0 and s.startswith(sep, i):
            part = "".join(buf).strip()
            if part:
                parts.append(part)
            buf = []
            i += len(sep)
        else:
            buf.append(char)
            i += 1

    if buf:
        parts.append("".join(buf).strip())

    return parts


def is_ground(term: Term) -> bool:
    match term:
        case Var():
            return False
        case Rule(lhs, rhs):
            return is_ground(lhs) and is_ground(rhs)
        case Node(head, args):
            return is_ground(head) and all(is_ground(arg) for arg in args)
        case _:
            return True
