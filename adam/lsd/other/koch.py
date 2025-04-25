"""
Use TRS to construct and print a Koch-like curve on a character grid.
Run with:
    python -m lsd.other.koch
"""

from lsd.term.seq import Seq
from lsd.trs import TermRewriteSystem


def generate_koch_seq(steps: int, axiom: Seq = Seq("F")) -> Seq:
    trs = TermRewriteSystem()
    trs.add_rule("F", Seq(*"F+F-F-F+F"))
    seq = axiom
    for _ in range(steps):
        seq = trs.rewrite_once(seq)
    assert isinstance(seq, Seq)
    return seq


def seq_to_points(seq: Seq) -> list[tuple[int, int]]:
    x, y = 0, 0
    dx, dy = 1, 0
    points: list[tuple[int, int]] = [(x, y)]
    for cmd in seq:
        if cmd == "F":
            x += dx
            y += dy
            points.append((x, y))
        elif cmd == "+":
            dx, dy = -dy, dx  # turn left 90°
        elif cmd == "-":
            dx, dy = dy, -dx  # turn right 90°
    return points


def print_koch(steps: int = 4) -> None:
    seq = generate_koch_seq(steps)
    points = seq_to_points(seq)
    xs, ys = zip(*points)
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width, height = max_x - min_x + 1, max_y - min_y + 1
    grid = [[" "] * width for _ in range(height)]
    for x, y in points:
        grid[max_y - y][x - min_x] = "X"
    for row in grid:
        print("".join(row))


def test_print() -> None:
    print_koch(steps=5)


if __name__ == "__main__":
    test_print()
