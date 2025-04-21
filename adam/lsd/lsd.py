from __future__ import annotations

import string
from collections import UserDict, UserString, defaultdict
from types import SimpleNamespace
from typing import Counter, Iterable, NamedTuple


class LetterStringDomain(UserString):
    """A domain of unique letters.

    Args:
        letters (str): The elements of the domain.
        allow_numbers (bool): Allow letters to be numbers; will still be treated as
            strings. Defaults to False.
        case_sensitive (bool): Allow uppercase letters. Defaults to False.
    """

    def __init__(
        self,
        source: str,
        allow_numbers: bool = False,
        case_sensitive: bool = False,
    ):
        config = LetterStringDomain.Config(allow_numbers, case_sensitive)
        LetterStringDomain.validate(source, config)
        super().__init__(source)
        self.config = config

    def check(self, letters: str) -> bool:
        for letter in letters:
            if letter not in self:
                raise ValueError("Letter %r does not belong to domain" % letter)

        return LetterStringDomain.validate(letters, self.config)

    @classmethod
    def validate(
        cls,
        source: str,
        config: LetterStringDomain.Config,
    ) -> bool:
        """Validate letters according to Config."""
        if not source:
            raise ValueError("Input string cannot be empty")
        if not (config.numbers or source.isalpha()):
            raise ValueError("Letters must only have alphabetic characters")
        if config.numbers and not source.isalnum():
            raise ValueError("Letters must only have alphabetic or numeric characters")
        for letter in source:
            if letter.isalpha() and not (config.case or source.islower()):
                raise ValueError("Letters must be lowercase")
        if len(set(source)) != len(source):
            raise ValueError("Letters must be unique")
        return True

    class Config(NamedTuple):
        """LSD Config"""

        numbers: bool
        case: bool


class LSD(SimpleNamespace):
    Alpha = LetterStringDomain(string.ascii_lowercase)
    Upper = LetterStringDomain(string.ascii_uppercase, case_sensitive=True)
    Vowel = LetterStringDomain("aeiou")
    Consonant = LetterStringDomain("bcdfghjklmnpqrstvwxyz")
    Mini = LetterStringDomain("abc")
    Number = LetterStringDomain(string.digits, allow_numbers=True)


class TransitionMap(UserDict):
    """Maps letter transitions and generates strings.

    Examples:

        >>> TransitionMap('abcabc')
        {'a': ['b', 'b'], 'b': ['c', 'c'], 'c': ['a', None]}

        >>> TransitionMap('abcabc').gen('c')
        'cabc'
    """

    def __init__(self, letters: str):
        d = defaultdict(list)
        for i in range(len(letters) - 1):
            d[letters[i]].append(letters[i + 1])
        d[letters[-1]].append(None)
        super().__init__({k: v for k, v in d.items()})

    def gen(self, first: str) -> str:
        """Generates a string starting with 'first' following transitions."""
        if len(first) != 1:
            raise ValueError("Input must be a single character")
        if first not in self:
            raise ValueError("Input character must be in the transition map")
        result = [first]
        current = first
        counter = Counter({k: 0 for k in self})
        while current in self and self[current]:
            next_char = self[current][counter[current]]
            if next_char is None:
                break
            result.append(next_char)
            counter[current] += 1
            current = next_char
        return "".join(result)


if __name__ == "__main__":
    for x in [
        LSD.Alpha,
        LSD.Upper,
        LSD.Vowel,
        LSD.Consonant,
        LSD.Number,
        LSD.Mini,
    ]:
        print(x, len(x))
