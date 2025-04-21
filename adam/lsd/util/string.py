import unittest
from collections import Counter
from typing import Optional

_distance_cache = {}


def distance(s1: str, s2: str) -> int:
    "Measure the Levenshtein distance between two strings."
    s1, s2 = s1.lower(), s2.lower()
    key = (s1, s2)
    if key in _distance_cache:
        return _distance_cache[key]
    len1, len2 = len(s1), len(s2)
    if len1 < len2:
        s1, s2, len1, len2 = s2, s1, len2, len1
    if len2 == 0:
        _distance_cache[key] = len1
        return len1
    row = list(range(len2 + 1))
    for i in range(1, len1 + 1):
        new_row = [i]
        for j in range(len2):
            new_row.append(min(row[j + 1] + 1, new_row[j] + 1, row[j] + (s1[i - 1] != s2[j])))
        row = new_row
    _distance_cache[key] = row[len2]
    return row[len2]


def similarity(s1: str, s2: str) -> float:
    "Returns the similarity between two strings. Returns 1.0 when the same; 0.0 completely different."
    if not s1 or not s2:
        return 1.0 if not s1 and not s2 else 0.0
    return 1.0 - distance(s1, s2) / max(len(s1), len(s2))


def closest(string: str, strings: list[str]) -> str:
    if not strings:
        raise ValueError("Strings list cannot be empty")
    return max(strings, key=lambda s: (similarity(string, s), -len(s)))


def letter_counts(s: str) -> Counter:
    return Counter(c.lower() for c in s if c.isalpha())


def least_common_letter(s: str) -> Optional[str]:
    counts = letter_counts(s)
    if not counts:
        return None
    min_count = min(counts.values())
    if min_count == 1:
        singles = [c for c, n in counts.items() if n == 1]
        if len(singles) == 1:
            return singles[0]
    return min(c for c, n in counts.items() if n == min_count)


def most_common_letter(s: str) -> Optional[str]:
    counts = letter_counts(s)
    return counts.most_common(1)[0][0] if counts else None


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

        if char in "[(":
            depth += 1
            buf.append(char)
            i += 1
            continue
        elif char in ")]":
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


def isfloat(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_balanced(string: str, open="(", close=")") -> bool:
    depth = 0
    for char in string:
        if char == open:
            depth += 1
        elif char == close:
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


if __name__ == "__main__":
    for s in ["aaaxa", "qmmmmm", "aaaaa"]:
        lc = least_common_letter(s) or "-"
        mc = most_common_letter(s) or "-"
        sim = similarity(s.replace(lc, mc, 1), s) if lc != "-" else 1.0
        print(f"{s:<6} {lc} -> {mc}: {sim:.2f}")
    unittest.main()
