import unittest

from lsd.util.string import (
    closest,
    distance,
    is_balanced,
    isfloat,
    least_common_letter,
    most_common_letter,
    similarity,
    split_at_depth,
)


class TestStringUtils(unittest.TestCase):
    def test_distance(self):
        self.assertEqual(distance("cat", "hat"), 1)
        self.assertEqual(distance("CAT", ""), 3)

    def test_similarity(self):
        self.assertAlmostEqual(similarity("cat", "hat"), 2 / 3)
        self.assertEqual(similarity("", ""), 1.0)

    def test_closest(self):
        self.assertEqual(closest("nat", ["cat", "hat", "rat"]), "cat")
        with self.assertRaises(ValueError):
            closest("cat", [])

    def test_least_common_letter(self):
        self.assertEqual(least_common_letter("qmmmmm"), "q")
        self.assertIsNone(least_common_letter("123"))

    def test_most_common_letter(self):
        self.assertEqual(most_common_letter("aaaxa"), "a")
        self.assertIsNone(most_common_letter(""))

    def test_balanced(self):
        self.assertTrue(is_balanced("()(())((()))"))

    def test_isfloat(self):
        self.assertTrue(isfloat("123.456"))
        self.assertFalse(isfloat("123.456.789"))

    def test_split_depth(self):
        self.assertEqual(
            split_at_depth("(a->b)->(b->a)", sep="->"),
            ["(a->b)", "(b->a)"],
        )
