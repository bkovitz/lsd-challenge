#!/usr/bin/env python3

"""
WORK IN PROGRESS

*Experimental* term-rewriting of letter-string domain (LSD) expressions.

Adam Neeley
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

# Basic lambdas

Succ = lambda char: chr(ord(char) + 1)
Last = lambda text: len(text) - 1


# Chunks


class Chunk(ABC):
    @abstractmethod
    def validate(self, text) -> bool:
        pass


@dataclass(frozen=True)
class Run(Chunk):
    map: Callable
    start: int
    end: int

    def validate(self, text) -> bool:
        a = text[self.start : self.end + 1]
        prev = a[0]

        for cur in a[1:]:
            if cur is not self.map(prev):
                return False
            prev = cur
        return True


# Chunk Modifiers


class ChunkModifier:
    def __init__(self, parent: Chunk, **kwargs):
        self.parent = parent
        self.kwargs = kwargs


# Tests


def test_run_modifier():
    run = Run(Succ, start=0, end=3)
    modifier = ChunkModifier(run, start=1)
    assert modifier.parent == run
    assert modifier.kwargs == {"start": 1}


def test_run():
    for s in ["abcd", "abcz"]:
        print(s, " ", Run(Succ, start=0, end=3).validate(s))


if __name__ == "__main__":

    test_run()
    test_run_modifier()
