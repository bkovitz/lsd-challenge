from .seq import Seq
from .term import Term, TermBase


class Node(TermBase):
    """
    Represents a function or operation with a head and variadic body.
    """

    __match_args__ = ("head", "body")

    def __init__(self, head: Term, *body: Term):
        self.head = head
        self.body = Seq(*body)

    def __repr__(self):
        return f"{self.head}({', '.join(map(str, self.body))})"

    def __eq__(self, other):
        return isinstance(other, Node) and self.head == other.head and self.body == other.body
