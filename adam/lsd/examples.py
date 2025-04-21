import unittest
from typing import NamedTuple

# Define the Example NamedTuple to structure the data
Example = NamedTuple(
    "Example",
    [
        ("a", str),  # Initial string A
        ("b", str),  # Target string B
        ("c", str),  # Initial string C
        ("d", str),  # Target string D
        ("description", str),  # A description of the transformation
    ],
)

# A list of examples for the "Appendix" category
_appendix = [
    Example("bbbb", "bbbbb", "bbb", "bbbb", "Append last letter"),
    Example("bbbb", "bbbbb", "eee", "eeee", "Append last letter"),
    Example("abcd", "abcde", "pqr", "pqrs", "Append next letter"),
    Example("edcd", "edcba", "wxy", "wxyz", "Append first letter"),
    Example("aaaxa", "aaaaa", "qmmmmm", "mmmmmm", "Replace oddball letter"),
    Example("abc", "abd", "pqrs", "pqrt", "Replace last letter with next"),
    Example("abc", "zyx", "def", "vwu", "Reverse string"),
    Example("mrgw", "wgrm", "ofq", "qfo", "Reverse string"),
    Example("abcdpqr", "pqrabcd", "ijkst", "kstij", "Rotate left by half"),
    Example("abcdpqr", "pqrabcd", "kkkmnop", "nopkkkm", "Rotate left by half"),
    Example("rgbum", "mrgbu", "tekx", "xtek", "Rotate right by one"),
]

# A list of examples for the "Other" category
_other = [
    Example("abc", "abccba", "xyz", "xyzzyx", "Mirror extension"),
    Example("abc", "cbaabc", "rstu", "utsrstu", "Symmetric appending"),
    Example("hi", "hihi", "go", "gogo", "Double character insert"),
    Example("abc", "abcbc", "xyz", "xyzyz", "Echo end pattern"),
    Example("abc", "bcd", "xyz", "yza", "Progressive shift"),
    Example("fog", "folg", "cat", "calt", "Insert fixed center"),
    Example("abc", "bca", "mno", "omn", "Fixed permutation"),
    Example("cake", "cbkf", "mate", "mbtf", "Replace vowel with next consonant"),
    Example("aaabbb", "ab", "zzzttt", "zt", "Reduce duplicates"),
    Example("redbox", "red", "bluecube", "blue", "Prefix mapping"),
    Example("abc", "abd", "cat", "cau", "Increment final letter"),
    Example("abc", "aNbNc", "xyz", "xNyNz", "Interleave fixed string"),
    Example("lion", "lioness", "actor", "actoress", "Add suffix"),
]


def get_examples() -> list:
    """Returns the combined list of example cases (both _appendix and _other)."""
    return _appendix + _other


if __name__ == "__main__":
    print("Letter String Domain (LSD) Examples")
    # Print each example with a formatted index
    for i, ex in enumerate(get_examples(), 1):
        print(f"{i:02d}. A: {ex.a:<8} B: {ex.b:<8} C: {ex.c:<8} D: {ex.d:<8} | {ex.description}")
