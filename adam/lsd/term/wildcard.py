from .term import TermBase


class Wildcard(TermBase):
    def __str__(self):
        return "_"

    def __eq__(self, other):
        return isinstance(other, Wildcard)

    def __hash__(self):
        return hash("_")
