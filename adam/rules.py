from env import Env
from parser import parse

rules: Env = Env(
    {
        parse("AdvanceLast[+A]"): parse("Join[Front[+A] Succ[Last[+A]]]"),
        parse("NewWorld[+A Blank]"): parse("NewWorld[AdvanceLast[+A]]"),
    }
)


def get_rules() -> Env:
    return rules
