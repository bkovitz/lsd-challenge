from __future__ import annotations

from collections import UserDict

from term import Term


class Env(UserDict):

    def set(self, key: Term, value: Term) -> None:
        self[key] = value

    def __repr__(self) -> str:
        return "Env(" + ", ".join(f"{k}: {v}" for k, v in self.items()) + ")"

    @staticmethod
    def combine(left: Env | None, right: Env | None) -> Env | None:
        if left is None or right is None:
            return None
        return Env(**left, **right)
