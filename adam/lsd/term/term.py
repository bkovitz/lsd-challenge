class TermBase: ...


type Term = int | str | float | TermBase | tuple["Term", ...]
