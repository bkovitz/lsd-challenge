from lsd.parser import parse_rule
from lsd.term import Rule

RULES = """
"""


def get_rules() -> list[Rule]:
    rules = [parse_rule(rule_str) for rule_str in RULES.splitlines() if rule_str]
    return rules
