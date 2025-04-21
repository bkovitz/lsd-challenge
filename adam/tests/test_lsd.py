import pytest

from lsd.lsd import TransitionMap, LetterStringDomain, LSD


def test_vowel_consonant_membership():
    # Vowels
    for v in ["a", "e", "i", "o", "u"]:
        assert v in LSD.Vowel
    assert "b" not in LSD.Vowel

    # Consonants
    for c in ["c", "d", "z"]:
        assert c in LSD.Consonant
    for nc in ["e", "a"]:
        assert nc not in LSD.Consonant


def test_letter_string_domain_valid_abc():
    domain = LetterStringDomain("abc")
    assert str(domain) == "abc"


def test_letter_string_domain_valid_AbC():
    domain = LetterStringDomain("AbC", case_sensitive=True)
    assert str(domain) == "AbC"


def test_letter_string_domain_valid_numbers():
    domain = LetterStringDomain("abc123", allow_numbers=True)
    assert str(domain) == "abc123"


def test_invalid_empty_domain():
    with pytest.raises(ValueError):
        LetterStringDomain("")


def test_duplicate_letters():
    with pytest.raises(ValueError):
        LetterStringDomain("aabc")


def test_forbidden_uppercase_without_case():
    with pytest.raises(ValueError):
        LetterStringDomain("ABC")


def test_forbidden_numbers_without_config():
    with pytest.raises(ValueError):
        LetterStringDomain("a1b2c3")


def test_domain_check_valid():
    domain = LetterStringDomain("abc")
    assert domain.check("abc") is True


def test_domain_check_invalid():
    domain = LetterStringDomain("abc")
    with pytest.raises(ValueError):
        domain.check("abcd")


def test_transition_map_generation_case1():
    tmap = TransitionMap("abcabc")
    assert tmap.gen("a") == "abcabc"


def test_transition_map_generation_case2():
    tmap = TransitionMap("abcabc")
    assert tmap.gen("b") == "bcabc"


def test_transition_map_generation_case3():
    tmap = TransitionMap("aaaaa")
    assert tmap.gen("a") == "aaaaa"


def test_transition_map_generation_case4():
    tmap = TransitionMap("xyz")
    assert tmap.gen("z") == "z"


def test_transition_map_invalid_start_length():
    tmap = TransitionMap("abc")
    with pytest.raises(ValueError):
        tmap.gen("ab")


def test_transition_map_start_not_in_map():
    tmap = TransitionMap("abc")
    with pytest.raises(ValueError):
        tmap.gen("z")


def test_transition_map_empty_creation():
    with pytest.raises(IndexError):
        TransitionMap("")
