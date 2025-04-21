from typing import Any, Iterable


def is_iter(o: Any) -> bool:
    """Is o iterable for for purposes of as_iter(), i.e. iterable but not a
    string, namedtuple, or dict?"""
    return isinstance(o, Iterable) and not isinstance(o, str) and not isinstance(o, dict)
