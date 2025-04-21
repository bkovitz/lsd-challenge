from typing import Any, Callable, Iterable


def is_str(value: Any) -> bool:
    """Check if the value is a string."""
    return isinstance(value, str)


def is_char(s: Any) -> bool:
    """Check if the value is a single character string."""
    return isinstance(s, str) and len(s) == 1


def is_any(_) -> bool:
    """Always returns True (used as a default condition)."""
    return True


def is_func(value: Any) -> bool:
    """Check if the value is callable (i.e., a function)."""
    return isinstance(value, Callable)


def is_iter(value: Any) -> bool:
    """Check if the value is iterable but not a string."""
    return not is_str(value) and isinstance(value, Iterable)
