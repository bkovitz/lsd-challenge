"""
Possible Syntax
"""


class Expr:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        if not (self.args or self.kwargs):
            return self.__class__.__name__
        return f"{self.__class__.__name__}[{' '.join(map(repr, self.args))}{' '.join(f'{k}={v}' for k, v in self.kwargs.items())}]"


class Chunk(Expr):
    pass


class Run(Expr):
    pass


class AdvanceAt(Expr):
    pass


class Last(Expr):
    pass


class Succ(Expr):
    pass


# Examples

e1 = Chunk(Run(Succ()), AdvanceAt(Last()))
e2 = Chunk(Run(Succ(), AdvanceAt(Last())))

if __name__ == "__main__":
    print(e1)
    print(e2)
