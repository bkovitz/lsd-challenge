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
        raise FizzleNoLength
    
    def paint(self, ctx: Context) -> Context:
        if (run := self.find_a(Run)) is not None:
            return run.paint(ctx)
        elif (s := self.find_a(str)) is not None:
            return ctx.with_canvas(s)
        else:
            raise NotImplementedError
            

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

    def paint(self, ctx: Context):
        length = ctx.get_length()
        elem = ctx.get_leftmost()
        result = [elem]
        for _ in range(1, length):
            elem = self.delta.generate_rhs(elem)
            result.append(elem)
        new_canvas = ''.join(result)
        return ctx.with_canvas(new_canvas)
"""
    def to_string(self, ch: Chunk) -> str:
        elem = ch.get_leftmost()
        length = ch.get_length()
        result = [elem]
        for _ in range(1, length):
            elem = self.delta.generate_rhs(elem)
            result.append(elem)
        return ''.join(result)
"""
class L:
    @classmethod
    def evaluate(cls, symbols: Dict[Any, Any]):
        return symbols.get(cls, None)

@dataclass(frozen=True)
class Succ:
    arg: Any

    @classmethod
    def detect(cls, s: str) -> bool: 
        for left, right in pairwise(s):
            if ord(left) + 1 != ord(right):
                return False
        return True

    def evaluate(self, symbols: Dict[Any, Any]):
        if (v := self.arg.evaluate(symbols)) is not None:
            if isinstance(v, str):
                result = chr(ord(v[0]) + 1)
                if result > 'z':
                    raise Fizzle
                return result
            else:
                raise NotImplementedError()
        else: 
            raise NotImplementedError('Fizzle')

@dataclass(frozen=True)
class Same:
    arg: Any

    @classmethod
    def detect(cls, s: str) -> bool:
        for left, right in pairwise(s):
            if left != right:
                return False
        return True

    def evaluate(self, symbols: Dict[Any, Any]):
        if (v := self.arg.evaluate(symbols)) is not None:
            if isinstance(v, str):
                return v
            else:
                raise NotImplementedError()
        else: 
            raise NotImplementedError('Fizzle')


@dataclass(frozen=True)
class Pred:
    arg: Any

    @classmethod
    def detect(cls, s: str) -> bool: 
        for left, right in pairwise(s):
            if ord(left) - 1 != ord(right):
                return False
        return True

    def evaluate(self, symbols: Dict[Any, Any]):
        if (v := self.arg.evaluate(symbols)) is not None:
            if isinstance(v, str):
                result = chr(ord(v[0]) - 1)
                if result < 'a':
                    raise Fizzle
                return result
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

class Fizzle(Exception):
    pass

class FizzleNoLength(Fizzle):
    pass

class Context:
    def __init__ (self, ch: Chunk, canvas: str):
        self.ch = ch
        self.canvas = canvas #TODO IMPLEMENT CANVAS CLASS
    
    def paint(self) -> Context:
        return self.ch.paint(self)

    def get_length(self) -> int:
        try:
            return len(self.canvas)
        except TypeError:
            return self.ch.get_length()
        # TODO What if canvas and Chunk have inconsistent lengths?

    def get_leftmost(self) -> str:
        if self.canvas is None:
           return self.ch.get_leftmost() 
        if self.canvas[0] != '_': # TODO What if canvas is length = 0?
            return self.canvas[0]
        else:
            raise NotImplementedError

    def with_canvas(self, canvas: str) -> Context:
        # TODO What if the new canvas is incompatible with the old canvas?
        return Context(self.ch, canvas)
# GLOBAL METHODS

def string_to_chunk(s: str):
    for detector in [Succ, Same, Pred]:
        if detector.detect(s):
            return Chunk(Run(Delta(L, detector(L))))
    return Chunk(s)
#    all_match = True
#    all_have_succ = True
#    for left, right in pairwise(s):
#        if left != right:
#            all_match = False
#        #if ord(left) + 1 != ord(right):
#            #return Chunk(s) # arbitrary Chunk
#    if all_match:
#        return Chunk(Run(Delta(L, Same(L))))
#    return Chunk(Run(Delta(L, Succ(L))))  # successor Chunk

def chunk_to_string(ch: Chunk, ctx: Optional[Context]=None) -> str:
    if ctx is None:
        ctx = Context(ch, None)
    return ctx.paint().canvas
    """
    # if there is a run object in chunk's args...
    if (run := ch.find_a(Run)) is not None:
        return run.to_string(ch)
    elif (s := ch.find_a(str)) is not None:
        return s
    else:
        raise NotImplementedError
    """
"""
def paint_on_canvas(ch: Chunk, canvas: str) -> str:
    ctx = make_context(ch, canvas)
    return ch.paint(ctx)
"""
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

    def test_bgl_to_string(self):
        expect = 'bgl'
        got = chunk_to_string(Chunk('bgl'))
        self.assertEqual(expect, got)

    def test_aaa(self):
        chunk = string_to_chunk('aaa')
        expect = Chunk(Run(Delta(L, Same(L))))
        self.assertEqual(chunk, expect)
    
    def test_regen_aaa(self):
        self.assertEqual(
            chunk_to_string(
                Chunk(Run(Delta(L, Same(L))), Leftmost('a'), Length(3))
            ),
            'aaa'
        )

    def test_cba(self):
        chunk = string_to_chunk('cba')
        expect = Chunk(Run(Delta(L, Pred(L))))
        self.assertEqual(chunk, expect)

    def test_regen_cba(self):
        self.assertEqual(
            chunk_to_string(
                Chunk(Run(Delta(L, Pred(L))), Leftmost('c'), Length(3))
            ),
            'cba'
        )

    def test_z_no_succ(self):
        with self.assertRaises(Fizzle):
            got = chunk_to_string(
                Chunk(Run(Delta(L, Succ(L))), Leftmost('z'), Length(2))
            )

    def test_z_no_succ2(self):
        with self.assertRaises(Fizzle):
            succ = Succ(L)
            symbols = {L: 'z'}
            shouldnt_work = succ.evaluate(symbols)
            
    def test_a_no_pred(self):
        with self.assertRaises(Fizzle):
            got = chunk_to_string(
                Chunk(Run(Delta(L, Pred(L))), Leftmost('a'), Length(2))
            )

    def test_a_no_pred2(self):
        with self.assertRaises(Fizzle):
            pred = Pred(L)
            symbols = {L: 'a'}
            shouldnt_work = pred.evaluate(symbols)
    
    def test_run_succ_with_blanks(self):
        ch = Chunk(Run(Delta(L, Succ(L))))
        ctx = Context(ch, 'a__')
        self.assertEqual(
            ctx.paint().canvas,
            'abc'
        )

""" NEXT TESTS:
Chunk[Run[L -> Succ[L]]] 'a__' -> 'abc'
Chunk[Run[L -> Succ[L]]] '___' -> Fizzle(need a letter)
Chunk[Run[L -> Succ[L]]] '_b_' -> 'abc'
Chunk[Run[L -> Succ[L]]] 'a...' -> Fizzle(need length)
Regen from Run[Same]  DONE
Regen from Run[Pred]  DONE
Regen from Run[Succ] from '__c'
Fizzle on Succ[z]  DONE
Fizzle on Pred[a]  DONE
#to_string for Same & Pred   
replace to_string() with paint()
string_to_chunk: add Pred

  'aaaihg'

"""
