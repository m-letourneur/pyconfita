import pytest
from pyconfita.type_casting import cast


def test_cast_default_to_string():
    """Test cast with default type (str)"""
    value = cast("hello")
    assert value == "hello"
    assert isinstance(value, str)


def test_cast_none_returns_none():
    """Test cast returns None when input is None"""
    assert cast(None) is None
    assert cast(None, str) is None
    assert cast(None, bool) is None
    assert cast(None, int) is None
    assert cast(None, float) is None


def test_cast_string_to_bool():
    """Test cast from string to bool"""
    # True cases
    assert cast("true", bool) is True
    assert cast("True", bool) is True
    assert cast("TRUE", bool) is True
    assert cast("t", bool) is True
    assert cast("T", bool) is True

    # False cases
    assert cast("false", bool) is False
    assert cast("False", bool) is False
    assert cast("f", bool) is False
    assert cast("F", bool) is False
    assert cast("", bool) is False
    assert cast("no", bool) is False


def test_cast_string_to_int():
    """Test cast from string to int"""
    assert cast("123", int) == 123
    assert isinstance(cast("123", int), int)

    assert cast("0", int) == 0
    assert cast("-42", int) == -42


def test_cast_string_to_float():
    """Test cast from string to float"""
    assert cast("10.5", float) == 10.5
    assert isinstance(cast("10.5", float), float)

    assert cast("10", float) == 10.0
    assert isinstance(cast("10", float), float)

    assert cast("-3.14", float) == -3.14
    assert cast("0.0", float) == 0.0


def test_cast_already_correct_type():
    """Test cast when value is already the correct type"""
    # Bool
    assert cast(True, bool) is True
    assert cast(False, bool) is False

    # Int
    assert cast(42, int) == 42
    assert isinstance(cast(42, int), int)

    # Float
    assert cast(3.14, float) == 3.14
    assert isinstance(cast(3.14, float), float)

    # String
    assert cast("hello", str) == "hello"


def test_cast_unsupported_type():
    """Test cast raises ValueError for unsupported types"""
    with pytest.raises(ValueError, match="Unsupported type conversion"):
        cast("value", list)

    with pytest.raises(ValueError, match="Unsupported type conversion"):
        cast("value", dict)

    with pytest.raises(ValueError, match="Unsupported type conversion"):
        cast("value", tuple)


def test_cast_non_string_to_different_type():
    """Test cast raises ValueError when trying to convert non-string to different type"""
    with pytest.raises(ValueError, match="Type conversion cannot be achieved"):
        cast(10, bool)

    with pytest.raises(ValueError, match="Type conversion cannot be achieved"):
        cast(3.14, int)

    # Note: bool is a subclass of int in Python, so cast(True, int) returns True
    # This is valid behavior and does not raise an error
    assert cast(True, int) is True
    assert cast(False, int) is False


def test_cast_invalid_string_format():
    """Test cast raises exception for invalid string formats"""
    with pytest.raises(ValueError):
        cast("not_a_number", int)

    with pytest.raises(ValueError):
        cast("not_a_float", float)
