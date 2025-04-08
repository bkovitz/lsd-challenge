from typing import Callable, NamedTuple, Type


Guard = Type | str | tuple["Guard", ...]


class Method(NamedTuple):
    name: str
    exec: Callable
    guards: tuple[Guard, ...] = ()

    @property
    def arity(self):
        return len(self.guards)

    def check_guards(self, *args):
        res = []
        for i, guard in enumerate(self.guards):
            if isinstance(guard, (str, int)):
                res.append(args[i].head and args[i].head == guard)
            else:
                res.append(isinstance(args[i], guard))
        return all(res)

    def __call__(self, *args):
        if len(args) != self.arity:
            raise ValueError(f"Expected {self.arity} arguments, got {len(args)}")
        if not self.check_guards(*args):
            raise ValueError(f"Expected type {self.guards}")
        return self.exec(*args)


def method(
    name: str,
    *guards: Guard,
    exec: Callable,
) -> Method:
    return Method(name, exec, guards)


METHODS = {
    "Add": method("add", (int, float), (int, float), exec=lambda a, b: a + b),
    "Sub": method("sub", (int, float), (int, float), exec=lambda a, b: a - b),
    "Mul": method("mul", (int, float), (int, float), exec=lambda a, b: a * b),
    "Div": method("div", (int, float), (int, float), exec=lambda a, b: a / b),
    "Max": method("max", (int, float), (int, float), exec=lambda *args: max(args)),
    "Join": method("join", str, str, exec=lambda *args: "".join(args)),
    "Succ": method("succ", str, exec=lambda letter: chr(ord(letter) + 1)),
    "Pred": method("pred", str, exec=lambda letter: chr(ord(letter) - 1)),
    "Last": method("last", str, exec=lambda letters: letters[-1]),
    "Front": method("front", str, exec=lambda letters: letters[:-1]),
}


def get_methods() -> dict[str, Method]:
    return METHODS
