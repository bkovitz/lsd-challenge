import pytest
from lsd.analogy import AnalogySolver
from lsd.examples import get_examples
from lsd.parser import parse_ensure


@pytest.fixture
def solver():
    return AnalogySolver()


@pytest.mark.parametrize(
    "A, B, C, expect_D, desc",
    [(a, b, c, d, desc) for a, b, c, d, desc in get_examples()],
)
@pytest.mark.skip("TODO")
def test_analogy(solver, A, B, C, expect_D, desc):
    A_term = parse_ensure(A)
    B_term = parse_ensure(B)
    C_term = parse_ensure(C)
    expected = parse_ensure(expect_D)

    print(desc)
    rule_or_method = solver.learn(A_term, B_term)
    assert rule_or_method is not None, f"Could not learn rule from {A} -> {B}"

    result = solver.apply(rule_or_method, C_term)
    assert (
        result == expected
    ), f"\nA: {A}\nB: {B}\nC: {C}\nExpected D: {expect_D}\nGot: {result}"
