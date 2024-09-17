import pytest
import operator

from typing_extensions import TypedDict, Annotated 

from kenkenpa.edges import StaticConditionalHandler
from kenkenpa.edges import compare_values

def test_conpare_values():
    assert compare_values("==",5,5) == True
    assert compare_values("==",5,4) == False
    assert compare_values("==","aaa","aaa") == True
    assert compare_values("==","aaa","aaba") == False
    assert compare_values("equals",5,5) == True
    assert compare_values("equals",5,4) == False
    assert compare_values("equals","aaa","aaa") == True
    assert compare_values("equals","aaa","aaba") == False
    assert compare_values("eq",5,5) == True
    assert compare_values("eq",5,4) == False
    assert compare_values("eq","aaa","aaa") == True
    assert compare_values("eq","aaa","aaba") == False

    assert compare_values("!=",5,5) == False
    assert compare_values("!=",5,4) == True
    assert compare_values("!=","aaa","aaa") == False
    assert compare_values("!=","aaa","aaba") == True
    assert compare_values("not_equals",5,5) == False
    assert compare_values("not_equals",5,4) == True
    assert compare_values("not_equals","aaa","aaa") == False
    assert compare_values("not_equals","aaa","aaba") == True
    assert compare_values("neq",5,5) == False
    assert compare_values("neq",5,4) == True
    assert compare_values("neq","aaa","aaa") == False
    assert compare_values("neq","aaa","aaba") == True

    assert compare_values(">",10,9)  == True
    assert compare_values(">",10,10)  == False
    assert compare_values(">","B","A")  == True
    assert compare_values(">","B","B")  == False
    assert compare_values("greater_than",10,9)  == True
    assert compare_values("greater_than",10,10)  == False
    assert compare_values("greater_than","B","A")  == True
    assert compare_values("greater_than","B","B")  == False
    assert compare_values("gt",10,9)  == True
    assert compare_values("gt",10,10)  == False
    assert compare_values("gt","B","A")  == True
    assert compare_values("gt","B","B")  == False

    assert compare_values(">=",10,9) == True
    assert compare_values(">=",10,10) == True
    assert compare_values(">=",10,11) == False
    assert compare_values(">=","B","A") == True
    assert compare_values(">=","B","B") == True
    assert compare_values(">=","B","C") == False
    assert compare_values("greater_than_or_equals",10,9) == True
    assert compare_values("greater_than_or_equals",10,10) == True
    assert compare_values("greater_than_or_equals",10,11) == False
    assert compare_values("greater_than_or_equals","B","A") == True
    assert compare_values("greater_than_or_equals","B","B") == True
    assert compare_values("greater_than_or_equals","B","C") == False    
    assert compare_values("gte",10,9) == True
    assert compare_values("gte",10,10) == True
    assert compare_values("gte",10,11) == False
    assert compare_values("gte","B","A") == True
    assert compare_values("gte","B","B") == True
    assert compare_values("gte","B","C") == False

    assert compare_values("<",9,10)  == True
    assert compare_values("<",10,10)  == False
    assert compare_values("<","A","B")  == True
    assert compare_values("<","B","B")  == False
    assert compare_values("less_than",9,10)  == True
    assert compare_values("less_than",10,10)  == False
    assert compare_values("less_than","A","B")  == True
    assert compare_values("less_than","B","B")  == False
    assert compare_values("lt",9,10)  == True
    assert compare_values("lt",10,10)  == False
    assert compare_values("lt","A","B")  == True
    assert compare_values("lt","B","B")  == False

    assert compare_values("<=",9,10) == True
    assert compare_values("<=",10,10) == True
    assert compare_values("<=",11,10) == False
    assert compare_values("<=","A","B") == True
    assert compare_values("<=","B","B") == True
    assert compare_values("<=","C","B") == False
    assert compare_values("less_than_or_equals",9,10) == True
    assert compare_values("less_than_or_equals",10,10) == True
    assert compare_values("less_than_or_equals",11,10) == False
    assert compare_values("less_than_or_equals","A","B") == True
    assert compare_values("less_than_or_equals","B","B") == True
    assert compare_values("less_than_or_equals","C","B") == False    
    assert compare_values("lte",9,10) == True
    assert compare_values("lte",10,10) == True
    assert compare_values("lte",11,10) == False
    assert compare_values("lte","A","B") == True
    assert compare_values("lte","B","B") == True
    assert compare_values("lte","C","B") == False

    exc_info = pytest.raises(ValueError, compare_values, "int", 1,1)
    assert str(exc_info.value) == "サポートされていない比較演算子: int"

class DummyType(TypedDict):
    dummy:str

def test_static_conditional_handler_init():
    def test_func():
        pass
    
    evaluate_functions = {
        "test_func":test_func
    }

    conditions = [
            {
                "expression": {
                    "eq": [{"type": "state_value", "name": "value"}, "10"],
                },
                "result": ["True"]
            },
            {"default": ["False"]} 
        ]

    handler = StaticConditionalHandler(
        conditions,
        evaluate_functions
    )

    assert handler.conditions == conditions
    assert handler.evaluate_functions == evaluate_functions

def test_static_conditional_handler_evaluate_expr():
    def func_a(state,config,**kwargs):
        if kwargs:
            return kwargs['args_a']
        return "func_return_value_a"
    
    evaluate_functions = {
        "func_name_a":func_a
    }
    conditions = []

    handler = StaticConditionalHandler(
        conditions,
        evaluate_functions
    )

    assert handler.conditions == conditions
    assert handler.evaluate_functions == evaluate_functions

    expr = {"eq": [10, 10]}
    assert handler._evaluate_expr(expr,{},{}) == True

    expr = {"and": [{"eq": [10, 10]}, {"eq": [10, 10]}, {"eq": [10, 10]}]}
    assert handler._evaluate_expr(expr,{},{}) == True

    expr = {"and": [{"eq": [10, 10]}, {"eq": [10, 10]}, {"eq": [10, 9]}]}
    assert handler._evaluate_expr(expr,{},{}) == False

    expr = {"or": [{"eq": [10, 10]}, {"eq": [10, 9]}, {"eq": [10, 9]}]}
    assert handler._evaluate_expr(expr,{},{}) == True

    expr = {"or": [{"eq": [10, 9]}, {"eq": [10, 9]}, {"eq": [10, 9]}]}
    assert handler._evaluate_expr(expr,{},{}) == False

    expr = {"not": {"eq": [10, 9]}}
    assert handler._evaluate_expr(expr,{},{}) == True
    expr = {"not": {"eq": [10, 10]}}
    assert handler._evaluate_expr(expr,{},{}) == False

    expr = {"eq": [{"type": "state_value", "name": "value_a"}, "result_a"]}
    state = {"value_a":"result_a"}
    assert handler._evaluate_expr(expr,state,{}) == True

    expr = {"eq": [{"type": "state_value", "name": "value_b1"},{"type": "config_value", "name": "value_b2"}]}
    state = {"value_b1":"result_b"}
    config = {"value_b2":"result_b"}
    assert handler._evaluate_expr(expr,state,config) == True

    expr = {"eq": [{"type": "config_value", "name": "value_c1"},{"type": "state_value", "name": "value_c2"}]}
    state = {"value_c2":"result_c"}
    config = {"value_c1":"result_c"}
    assert handler._evaluate_expr(expr,state,config) == True

    expr = {"eq": [{"type": "function", "name": "func_name_a"}, "func_return_value_a"]}
    assert handler._evaluate_expr(expr,{},{}) == True

    expr = {"eq": [{"type": "function", "name": "func_name_a","args":{"args_a":"args_value"}}, "args_value"]}
    assert handler._evaluate_expr(expr,{},{}) == True
    expr = {"eq": [ "args_value", {"type": "function", "name": "func_name_a","args":{"args_a":"args_value"}}]}
    assert handler._evaluate_expr(expr,{},{}) == True

    expr = {"error_op": [10, 10]}
    exc_info = pytest.raises(ValueError, handler._evaluate_expr, expr, {},{})
    assert str(exc_info.value) == "サポートされていない演算: error_op"

    expr = {"eq": [{"type": "error_type", "name": "func_name_a"}, "func_return_value_a"]}
    exc_info = pytest.raises(ValueError, handler._evaluate_expr, expr, {},{})
    assert str(exc_info.value) == "サポートされていないタイプ: error_type"

    expr = {"eq": [{"type": "function", "name": "error_function_name"}, "func_return_value_a"]}
    exc_info = pytest.raises(ValueError, handler._evaluate_expr, expr, {},{})
    assert str(exc_info.value) == "関数 error_function_name が evaluate_functions に見つかりません"