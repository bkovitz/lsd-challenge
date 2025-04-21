import random
import unittest

DEFAULT_RANDOM_SEED = 42
DEFAULT_RANDOM_STRING_LENGTH = 10
DEFAULT_RANDOM_STRINGS_COUNT = 10


def random_letter() -> str:
    return chr(random.randint(ord("a"), ord("z")))


def random_string(length: int = DEFAULT_RANDOM_STRING_LENGTH) -> str:
    return "".join(random_letter() for _ in range(length))


def random_strings(
    length: int = DEFAULT_RANDOM_STRING_LENGTH,
    count: int = DEFAULT_RANDOM_STRINGS_COUNT,
    seed: int = DEFAULT_RANDOM_SEED,
) -> list[str]:
    random.seed(seed)
    return [random_string(length) for _ in range(count)]


class TestRandom(unittest.TestCase):

    def test_random_strings(self):
        strings = random_strings(length=5, count=3, seed=42)
        expected = random_strings(length=5, count=3, seed=42)
        self.assertEqual(strings, expected)
        self.assertEqual(len(strings), 3)
        self.assertTrue(all(len(s) == 5 for s in strings))
