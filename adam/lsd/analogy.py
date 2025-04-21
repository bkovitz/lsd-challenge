from dataclasses import dataclass, field

from lsd.term import Rule, Term
from lsd.term.rule import TermRule
from lsd.trs import TermRewriteSystem


@dataclass(frozen=True)
class AnalogySolver:
    """
    A class that attempts to solve analogies between two strings by learning a transformation rule
    from one string (A) to another (B) using a term-rewriting system.

    This class is a work-in-progress (WIP) for learning and solving analogies. It works by:
    - Learning the transformation from string A to string B.
    - Solving a given analogy using the learned rules.

    Attributes:
        engine (TermRewriteSystem): The term-rewriting system used to rewrite terms.
        chunks (dict): A dictionary of chunks (currently unused in the provided code).
    """

    # The term-rewriting engine used for solving the analogy
    engine: TermRewriteSystem = field(default_factory=TermRewriteSystem)
    # The dictionary that will hold "chunks" for analogy (currently unused)
    chunks: dict[str, Rule] = field(default_factory=dict)

    def learn(self, A: str, B: str, op_name: str) -> Rule:
        """
        Learns the transformation rule from string A to string B.

        This method attempts to rewrite string A into string B using the term-rewriting engine.
        If the rewrite fails or no rules are fired during the rewrite, an error is raised.

        Args:
            A (str): The starting string (the "source" string).
            B (str): The target string that A should transform into.
            op_name (str): The operation name used during the learning process (not used in this method).

        Returns:
            Rule: The learned rule (although this method does not currently return a rule).

        Raises:
            ValueError: If the rewrite of A does not result in B.
            RuntimeError: If no rules were fired during the rewrite.
        """
        self.engine.trace.clear()  # Clear any existing trace from previous rewrites

        # Perform the rewrite of A
        got = self.engine.rewrite(A)

        # Check if the rewrite result matches the expected output (B)
        if got != B:
            raise ValueError(f"Failed to learn: got {got!r}, expected {B!r}")

        # If no rules were fired during the rewrite, raise an error
        if not self.engine.trace:
            raise RuntimeError("No rules fired during rewrite")

        return TermRule("_", "_")

    def solve(self, C: str) -> Term:
        """
        Solves the analogy by rewriting the given string C using the learned transformation.

        Args:
            C (str): The string to transform based on the learned analogy.

        Returns:
            Term: The rewritten term (result of applying the learned rule to string C).
        """
        return self.engine.rewrite(C)
