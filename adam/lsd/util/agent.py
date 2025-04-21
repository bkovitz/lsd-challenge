import unittest
from abc import ABC, abstractmethod
from collections import Counter

from .string import least_common_letter, most_common_letter, similarity


class Agent(ABC):
    def __init__(self, sensitivity: float = 0.8):
        self.sensitivity = min(max(sensitivity, 0), 1)

    @abstractmethod
    def cond(self, string: str) -> bool: ...

    @abstractmethod
    def edit(self, string: str) -> str: ...


class OddballAgent(Agent):
    def cond(self, string: str) -> bool:
        modified = self.edit(string)
        return string != modified and similarity(modified, string) >= self.sensitivity

    def edit(self, string: str) -> str:
        oddball = least_common_letter(string)
        if not oddball:
            return string
        replacement = most_common_letter(string) or oddball
        return "".join(replacement if c.lower() == oddball else c for c in string)


class MostlyAgent(Agent):
    def cond(self, string: str) -> bool:
        if not string:
            return False
        counts = Counter(c.lower() for c in string if c.isalpha())
        return (
            counts.most_common(1)[0][1] / sum(counts.values()) >= self.sensitivity
            if counts
            else False
        )

    def edit(self, string: str) -> str:
        mc = most_common_letter(string)
        return string if not mc else "".join(mc if c.lower() != mc else c for c in string)


class PredAgent(Agent):
    def cond(self, string: str) -> bool:
        return len(string) > 0 and "a" not in string

    def edit(self, string: str) -> str:
        return "".join([chr(ord(l) - 1) for l in string])


class SuccAgent(Agent):
    def cond(self, string: str) -> bool:
        return len(string) > 0 and "z" not in string

    def edit(self, string: str) -> str:
        return "".join([chr(ord(l) + 1) for l in string])


class AppendAgent(Agent):
    def cond(self, string: str) -> bool:
        if len(string) < 2:
            return False
        return similarity(string + string[-1], string) >= self.sensitivity

    def edit(self, string: str) -> str:
        return string + (string[-1] if string else "")


class ReplacePosAgent(Agent):
    def __init__(self, sensitivity: float = 0.8, pos: int = -1):
        super().__init__(sensitivity)
        self.pos = pos

    def cond(self, string: str) -> bool:
        if not string or abs(self.pos) > len(string):
            return False
        modified = self.edit(string)
        return similarity(modified, string) >= self.sensitivity

    def edit(self, string: str) -> str:
        if not string or abs(self.pos) > len(string):
            return string
        mc = most_common_letter(string) or string[0]
        pos = self.pos if self.pos >= 0 else len(string) + self.pos
        return string[:pos] + mc + string[pos + 1 :]


class TestAgent(unittest.TestCase):
    def test_pred_agent(self):
        agent = PredAgent()
        self.assertTrue(agent.cond("xyz"))
        self.assertEqual(agent.edit("xyz"), "wxy")

    def test_succ_agent(self):
        agent = SuccAgent()
        self.assertTrue(agent.cond("abc"))
        self.assertEqual(agent.edit("abc"), "bcd")

    def test_oddball_agent(self):
        agent = OddballAgent(0.7)
        self.assertTrue(agent.cond("qmmmmm"))
        self.assertEqual(agent.edit("aaaxa"), "aaaaa")

    def test_mostly_agent(self):
        agent = MostlyAgent(0.6)
        self.assertTrue(agent.cond("aaaba"))
        self.assertEqual(agent.edit("aaaxa"), "aaaaa")

    def test_append_agent(self):
        agent = AppendAgent(0.7)
        self.assertTrue(agent.cond("eee"))
        self.assertEqual(agent.edit("eee"), "eeee")

    def test_replace_pos_agent(self):
        agent = ReplacePosAgent(0.7, -1)
        self.assertTrue(agent.cond("aaaxa"))
        self.assertEqual(agent.edit(""), "")


if __name__ == "__main__":
    unittest.main()
