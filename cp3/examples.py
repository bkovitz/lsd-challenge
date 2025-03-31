"""
Sample problems from the appendix of the dissertation.
"""

from collections import namedtuple

Example = namedtuple("Example", "a b c d")

_examples = [
    Example("bbbb", "bbbbb", "bbb", "bbbb"),  # 1
    Example("bbbb", "bbbbb", "eee", "eeee"),
    Example("abcd", "abcde", "pqr", "pqrs"),
    Example("edcd", "edcba", "wxy", "wxyz"),
    Example("aaaxa", "aaaaa", "qmmmmm", "mmmmmm"),
    Example("abc", "abd", "pqrs", "pqrt"),
    Example("abc", "zyx", "def", "vwu"),
    Example("mrgw", "wgrm", "ofq", "qfo"),
    Example("abcdpqr", "pqrabcd", "ijkst", "kstij"),
    Example("abcdpqr", "pqrabcd", "kkkmnop", "nopkkkm"),
    Example("rgbum", "mrgbu", "tekx", "xtek"),  # 11
    # TODO add more examples
]

if __name__ == "__main__":
    print("Examples:")
    for example in _examples:
        print(example)
