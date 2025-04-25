"""
Use TRS to construct Cantor set.
Print Cantor set to screen.

Run with:
    python -m lsd.other.cantor
"""

from lsd.term.seq import Seq
from lsd.trs import TermRewriteSystem

trs = TermRewriteSystem()
trs.add_rule("A", Seq("A", "B", "A"))
trs.add_rule("B", Seq("B", "B", "B"))


def generate_cantor(
    steps: int,
    axiom: Seq = Seq("A"),
) -> list[Seq]:
    sequences: list[Seq] = []
    current = axiom
    for _ in range(steps):
        current = trs.rewrite_once(current)
        assert isinstance(current, Seq)
        sequences.append(current)
    return sequences


def render_sequence(
    sequence: Seq,
    scale: int,
) -> str:
    mapping = {"A": "X" * scale, "B": " " * scale}
    return "".join(mapping[char] for char in sequence)


def print_cantor(steps: int = 4) -> None:
    sequences = generate_cantor(steps)
    total = len(sequences)
    for idx, seq in enumerate(sequences):
        scale = 3 ** (total - idx - 1)
        line = render_sequence(seq, scale)
        print(line)


def test_print() -> None:
    print_cantor(steps=4)


if __name__ == "__main__":
    test_print()
