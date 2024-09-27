import pytest
from typing_extensions import TypedDict
from kenkenpa.edges import compare_values

# Test compare_values function
def test_compare_values_equality():
    assert compare_values("==", 5, 5) is True
    assert compare_values("==", 5, 4) is False
    assert compare_values("==", "aaa", "aaa") is True
    assert compare_values("==", "aaa", "aaba") is False
    assert compare_values("equals", 5, 5) is True
    assert compare_values("equals", 5, 4) is False
    assert compare_values("equals", "aaa", "aaa") is True
    assert compare_values("equals", "aaa", "aaba") is False
    assert compare_values("eq", 5, 5) is True
    assert compare_values("eq", 5, 4) is False
    assert compare_values("eq", "aaa", "aaa") is True
    assert compare_values("eq", "aaa", "aaba") is False

def test_compare_values_inequality():
    assert compare_values("!=", 5, 5) is False
    assert compare_values("!=", 5, 4) is True
    assert compare_values("!=", "aaa", "aaa") is False
    assert compare_values("!=", "aaa", "aaba") is True
    assert compare_values("not_equals", 5, 5) is False
    assert compare_values("not_equals", 5, 4) is True
    assert compare_values("not_equals", "aaa", "aaa") is False
    assert compare_values("not_equals", "aaa", "aaba") is True
    assert compare_values("neq", 5, 5) is False
    assert compare_values("neq", 5, 4) is True
    assert compare_values("neq", "aaa", "aaa") is False
    assert compare_values("neq", "aaa", "aaba") is True

def test_compare_values_greater_than():
    assert compare_values(">", 10, 9) is True
    assert compare_values(">", 10, 10) is False
    assert compare_values(">", "B", "A") is True
    assert compare_values(">", "B", "B") is False
    assert compare_values("greater_than", 10, 9) is True
    assert compare_values("greater_than", 10, 10) is False
    assert compare_values("greater_than", "B", "A") is True
    assert compare_values("greater_than", "B", "B") is False
    assert compare_values("gt", 10, 9) is True
    assert compare_values("gt", 10, 10) is False
    assert compare_values("gt", "B", "A") is True
    assert compare_values("gt", "B", "B") is False

def test_compare_values_greater_than_or_equal():
    assert compare_values(">=", 10, 9) is True
    assert compare_values(">=", 10, 10) is True
    assert compare_values(">=", 10, 11) is False
    assert compare_values(">=", "B", "A") is True
    assert compare_values(">=", "B", "B") is True
    assert compare_values(">=", "B", "C") is False
    assert compare_values("greater_than_or_equals", 10, 9) is True
    assert compare_values("greater_than_or_equals", 10, 10) is True
    assert compare_values("greater_than_or_equals", 10, 11) is False
    assert compare_values("greater_than_or_equals", "B", "A") is True
    assert compare_values("greater_than_or_equals", "B", "B") is True
    assert compare_values("greater_than_or_equals", "B", "C") is False
    assert compare_values("gte", 10, 9) is True
    assert compare_values("gte", 10, 10) is True
    assert compare_values("gte", 10, 11) is False
    assert compare_values("gte", "B", "A") is True
    assert compare_values("gte", "B", "B") is True
    assert compare_values("gte", "B", "C") is False

def test_compare_values_less_than():
    assert compare_values("<", 9, 10) is True
    assert compare_values("<", 10, 10) is False
    assert compare_values("<", "A", "B") is True
    assert compare_values("<", "B", "B") is False
    assert compare_values("less_than", 9, 10) is True
    assert compare_values("less_than", 10, 10) is False
    assert compare_values("less_than", "A", "B") is True
    assert compare_values("less_than", "B", "B") is False
    assert compare_values("lt", 9, 10) is True
    assert compare_values("lt", 10, 10) is False
    assert compare_values("lt", "A", "B") is True
    assert compare_values("lt", "B", "B") is False

def test_compare_values_less_than_or_equal():
    assert compare_values("<=", 9, 10) is True
    assert compare_values("<=", 10, 10) is True
    assert compare_values("<=", 11, 10) is False
    assert compare_values("<=", "A", "B") is True
    assert compare_values("<=", "B", "B") is True
    assert compare_values("<=", "C", "B") is False
    assert compare_values("less_than_or_equals", 9, 10) is True
    assert compare_values("less_than_or_equals", 10, 10) is True
    assert compare_values("less_than_or_equals", 11, 10) is False
    assert compare_values("less_than_or_equals", "A", "B") is True
    assert compare_values("less_than_or_equals", "B", "B") is True
    assert compare_values("less_than_or_equals", "C", "B") is False
    assert compare_values("lte", 9, 10) is True
    assert compare_values("lte", 10, 10) is True
    assert compare_values("lte", 11, 10) is False
    assert compare_values("lte", "A", "B") is True
    assert compare_values("lte", "B", "B") is True
    assert compare_values("lte", "C", "B") is False

def test_compare_values_invalid_operator():
    exc_info = pytest.raises(ValueError, compare_values, "int", 1, 1)
    assert str(exc_info.value) == "Unsupported comparison operator: int"

