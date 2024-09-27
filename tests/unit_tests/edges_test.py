import pytest
from typing_extensions import TypedDict
from langgraph.types import Send
from kenkenpa.edges import ConfigurableConditionalHandler

class DummyType(TypedDict):
    dummy: str

def test_handler_initialization():
    def test_func():
        pass

    evaluate_functions = {"test_func": test_func}
    conditions = [
        {
            "expression": {"eq": [{"type": "state_value", "name": "value"}, "10"]},
            "result": ["True"]
        },
        {"default": ["False"]}
    ]

    handler = ConfigurableConditionalHandler(conditions, evaluate_functions)

    assert handler.conditions == conditions
    assert handler.evaluate_functions == evaluate_functions

def test_handler_evaluate_expr_basic_operations():
    def func_a(state, config, **kwargs):
        if kwargs:
            return kwargs['args_a']
        return "func_return_value_a"

    evaluate_functions = {"func_name_a": func_a}
    conditions = []

    handler = ConfigurableConditionalHandler(conditions, evaluate_functions)

    assert handler.conditions == conditions
    assert handler.evaluate_functions == evaluate_functions

    expr = {"eq": [10, 10]}
    assert handler._evaluate_expr(expr, {}, {}) == True

    expr = {"and": [{"eq": [10, 10]}, {"eq": [10, 10]}, {"eq": [10, 10]}]}
    assert handler._evaluate_expr(expr, {}, {}) == True

    expr = {"and": [{"eq": [10, 10]}, {"eq": [10, 10]}, {"eq": [10, 9]}]}
    assert handler._evaluate_expr(expr, {}, {}) == False

    expr = {"or": [{"eq": [10, 10]}, {"eq": [10, 9]}, {"eq": [10, 9]}]}
    assert handler._evaluate_expr(expr, {}, {}) == True

    expr = {"or": [{"eq": [10, 9]}, {"eq": [10, 9]}, {"eq": [10, 9]}]}
    assert handler._evaluate_expr(expr, {}, {}) == False

    expr = {"not": {"eq": [10, 9]}}
    assert handler._evaluate_expr(expr, {}, {}) == True

    expr = {"not": {"eq": [10, 10]}}
    assert handler._evaluate_expr(expr, {}, {}) == False

def test_handler_evaluate_expr_with_state_and_config():
    def func_a(state, config, **kwargs):
        if kwargs:
            return kwargs['args_a']
        return "func_return_value_a"

    evaluate_functions = {"func_name_a": func_a}
    conditions = []

    handler = ConfigurableConditionalHandler(conditions, evaluate_functions)

    expr = {"eq": [{"type": "state_value", "name": "value_a"}, "result_a"]}
    state = {"value_a": "result_a"}
    assert handler._evaluate_expr(expr, state, {}) == True

    expr = {"eq": [{"type": "state_value", "name": "value_b1"}, {"type": "config_value", "name": "value_b2"}]}
    state = {"value_b1": "result_b"}
    config = {"configurable": {"value_b2": "result_b"}}
    assert handler._evaluate_expr(expr, state, config) == True

    expr = {"eq": [{"type": "config_value", "name": "value_c1"}, {"type": "state_value", "name": "value_c2"}]}
    state = {"value_c2": "result_c"}
    config = {"configurable": {"value_c1": "result_c"}}
    assert handler._evaluate_expr(expr, state, config) == True

def test_handler_evaluate_expr_with_functions():
    def func_a(state, config, **kwargs):
        if kwargs:
            return kwargs['args_a']
        return "func_return_value_a"

    evaluate_functions = {"func_name_a": func_a}
    conditions = []

    handler = ConfigurableConditionalHandler(conditions, evaluate_functions)

    expr = {"eq": [{"type": "function", "name": "func_name_a"}, "func_return_value_a"]}
    assert handler._evaluate_expr(expr, {}, {}) == True

    expr = {"eq": [{"type": "function", "name": "func_name_a", "args": {"args_a": "args_value"}}, "args_value"]}
    assert handler._evaluate_expr(expr, {}, {}) == True

    expr = {"eq": ["args_value", {"type": "function", "name": "func_name_a", "args": {"args_a": "args_value"}}]}
    assert handler._evaluate_expr(expr, {}, {}) == True

def test_handler_evaluate_expr_with_errors():
    def func_a(state, config, **kwargs):
        if kwargs:
            return kwargs['args_a']
        return "func_return_value_a"

    evaluate_functions = {"func_name_a": func_a}
    conditions = []

    handler = ConfigurableConditionalHandler(conditions, evaluate_functions)

    expr = {"error_op": [10, 10]}
    exc_info = pytest.raises(ValueError, handler._evaluate_expr, expr, {}, {})
    assert str(exc_info.value) == "Unsupported operation: error_op"

    expr = {"eq": [{"type": "error_type", "name": "func_name_a"}, "func_return_value_a"]}
    exc_info = pytest.raises(ValueError, handler._evaluate_expr, expr, {}, {})
    assert str(exc_info.value) == "Unsupported type: error_type"

    expr = {"eq": [{"type": "function", "name": "error_function_name"}, "func_return_value_a"]}
    exc_info = pytest.raises(ValueError, handler._evaluate_expr, expr, {}, {})
    assert str(exc_info.value) == "The function error_function_name cannot be found in evaluate_functions."

    exc_info = pytest.raises(ValueError, handler._evaluate_expr, "NON_DICT_DATA", {}, {})
    assert str(exc_info.value) == "The formula must be a dictionary."

def test_handler_evaluate_conditions_basic():
    evaluate_functions = {}
    conditions = []

    handler = ConfigurableConditionalHandler(conditions, evaluate_functions)

    conditions = [
        {
            "expression": {
                "and": [
                    {"eq": ["10", "10"]},
                    {"eq": ["10", "10"]},
                    {"eq": ["10", "10"]}
                ]
            },
            "result": "Result_Value"
        },
        {"default": "Default_Value"}
    ]

    assert handler._evaluate_conditions(conditions, {}, {}) == ["Result_Value"]

    conditions = [
        {
            "expression": {
                "and": [
                    {"eq": ["10", "9"]},
                    {"eq": ["10", "9"]},
                    {"eq": ["10", "9"]}
                ]
            },
            "result": "Result_Value"
        },
        {"default": "Default_Value"}
    ]

    assert handler._evaluate_conditions(conditions, {}, {}) == ["Default_Value"]

def test_handler_evaluate_conditions_with_multiple_results():
    evaluate_functions = {}
    conditions = []

    handler = ConfigurableConditionalHandler(conditions, evaluate_functions)

    conditions = [
        {
            "expression": {
                "and": [
                    {"eq": ["10", "10"]}
                ]
            },
            "result": "Result_Value_A"
        },
        {
            "expression": {
                "and": [
                    {"eq": ["10", "10"]}
                ]
            },
            "result": "Result_Value_B"
        },
        {"default": "Default_Value"}
    ]

    assert handler._evaluate_conditions(conditions, {}, {}) == ["Result_Value_A", "Result_Value_B"]

def test_handler_evaluate_conditions_with_nested_expressions():
    evaluate_functions = {}
    conditions = []

    handler = ConfigurableConditionalHandler(conditions, evaluate_functions)

    conditions = [
        {
            "expression": {
                "and": [
                    {
                        "or": [
                            {
                                "and": [
                                    {"eq": ["10", "10"]}
                                ]
                            },
                            {"eq": ["10", "10"]}
                        ]
                    },
                    {"eq": ["10", "10"]}
                ]
            },
            "result": "Result_Value"
        },
        {"default": "Default_Value"}
    ]

    assert handler._evaluate_conditions(conditions, {}, {}) == ["Result_Value"]

def test_handler_evaluate_conditions_with_default():
    evaluate_functions = {}
    conditions = []

    handler = ConfigurableConditionalHandler(conditions, evaluate_functions)

    conditions = [
        {
            "expression": {
                "and": [
                    {"eq": ["10", "9"]}
                ]
            },
            "result": ["Result_Value"]
        }
    ]

    exc_info = pytest.raises(ValueError, handler._evaluate_conditions, conditions, {}, {})
    assert str(exc_info.value) == "No matching conditions were found, and no default function was provided."

def test_handler_evaluate_conditions_with_function_result():
    def return_function(state, config, **kwargs):
        return Send("node", {"arg": "test"})

    evaluate_functions = {"return_function": return_function}
    conditions = []

    handler = ConfigurableConditionalHandler(conditions, evaluate_functions)

    conditions = [
        {
            "expression": {"eq": ["10", "10"]},
            "result": {"type": "function", "name": "return_function"}
        },
        {"default": ["ERROR"]}
    ]

    expected_result = [Send("node", {"arg": "test"})]
    assert handler._evaluate_conditions(conditions, {}, {}) == expected_result

    conditions = [
        {
            "expression": {"eq": ["10", "9"]},
            "result": ["ERROR"]
        },
        {"default": {"type": "function", "name": "return_function"}}
    ]

    expected_result = [Send("node", {"arg": "test"})]
    assert handler._evaluate_conditions(conditions, {}, {}) == expected_result

def test_handler_call():
    evaluate_functions = {}
    conditions = [
        {
            "expression": {
                "and": [
                    {"eq": ["10", "10"]},
                    {"eq": ["10", "10"]},
                    {"eq": ["10", "10"]}
                ]
            },
            "result": ["Result_Value"]
        },
        {"default": "Default_Value"}
    ]

    handler = ConfigurableConditionalHandler(conditions, evaluate_functions)

    assert handler.__call__({}, {}) == ["Result_Value"]