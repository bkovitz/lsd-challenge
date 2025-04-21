import unittest

from lsd.env import Env


class TestEnv(unittest.TestCase):
    def test_bind(self):
        a = Env(A=1)
        assert a.bind("B", 2) == Env(A=1, B=2)

    def test_combine(self):
        a = Env(A=1)
        b = Env(B=2)
        c = Env.combine(a, b)
        self.assertEqual(c, Env(A=1, B=2))
