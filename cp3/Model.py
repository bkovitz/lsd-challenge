from __future__ import annotations
import unittest
from dataclasses import dataclass, field
from itertools import pairwise
from typing import Any, Tuple, Type, Optional, Dict
from util import force_setattr


@dataclass(frozen=True)
class Chunk:
    args: frozenset[Any]

    def __init__(self, *args: Any):
        force_setattr(self, 'args', frozenset(args))

    def find_a(self, clas: Type) -> Optional[Any]:
        for arg in self.args:
            if isinstance(arg, clas):
                return arg
        return None

    def get_leftmost(self) -> Optional[Any]:
        if l := self.find_a(Leftmost):
            return l.x
        return None

    def get_length(self) -> Optional[int]:
        if l := self.find_a(Length):
            return l.n
        return None

@dataclass(frozen=True)
class Delta:
    lhs: Any
    rhs: Any

    def generate_rhs(self, given_lhs) -> Any:
        symbols = match_lhs(self.lhs, given_lhs)
        return self.rhs.evaluate(symbols)

@dataclass(frozen=True)
class Run:
    delta: Delta

    def to_string(self, ch: Chunk) -> str:
        elem = ch.get_leftmost()
        length = ch.get_length()
        result = [elem]
        for _ in range(1, length):
            elem = self.delta.generate_rhs(elem)
            result.append(elem)
        return ''.join(result)

class L:
    @classmethod
    def evaluate(cls, symbols: Dict[Any, Any]):
        return symbols.get(cls, None)

@dataclass(frozen=True)
class Succ:
    arg: Any

    def evaluate(self, symbols: Dict[Any, Any]):
        if (v := self.arg.evaluate(symbols)) is not None:
            if isinstance(v, str):
                return chr(ord(v[0]) + 1)
            else:
                raise NotImplementedError()
        else: 
            raise NotImplementedError('Fizzle')


@dataclass(frozen=True)
class Length:
    n: int

@dataclass(frozen=True)
class Leftmost:
    x: Any # leftmost "thing" (letter, chunk, ...)


# GLOBAL METHODS

def string_to_chunk(s: str):
    for left, right in pairwise(s):
        if ord(left) + 1 != ord(right):
            return Chunk(s) # arbitrary Chunk
    return Chunk(Run(Delta(L, Succ(L))))  # successor Chunk

def chunk_to_string(ch: Chunk) -> str:
    # if there is a run object in chunk's args...
    if (run := ch.find_a(Run)) is not None:
        return run.to_string(ch)
    else:
        return 'abc'

def match_lhs(lhs: Any, given_lhs: Any) -> dict[Any, Any]:
    if lhs is L:
        return { L: given_lhs }
    else:
        raise NotImplementedError()


# TESTS
class TestChunk(unittest.TestCase):
    
    def test_abc(self):
        chunk = string_to_chunk('abc')
        expect = Chunk(Run(Delta(L, Succ(L))))
        self.assertEqual(chunk, expect)

    def test_bgl(self):
        chunk = string_to_chunk('bgl')
        expect = Chunk('bgl')
        self.assertEqual(chunk, expect)

    def test_blanks(self):
        expect = 'abc'
        got = chunk_to_string(
            Chunk(Run(Delta(L, Succ(L))), Leftmost('a'), Length(3))
        )
        self.assertEqual(expect, got)

""" NEXT TESTS:
Chunk[Run[L -> Succ[L]]] 'a__' -> 'abc'
Chunk[Run[L -> Succ[L]]] '___' -> Fizzle(need a letter)
Chunk[Run[L -> Succ[L]]] '_b_' -> 'abc'
Chunk[Run[L -> Succ[L]]] 'a...' -> Fizzle(need length)
"""
