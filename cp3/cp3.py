
def parse_rules(rules_text: str) -> Iterable[Rule]:
    for line in as_stripped_lines(rules_text):
        yield parse_rule(line)

def parse_rule(line: str) -> Rule:
    str = line.split('->')  # HACK: 
    if len(str) != 2:
