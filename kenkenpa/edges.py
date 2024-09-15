"""
This module provides functionality to add static conditional edges based on given
conditions and evaluation functions.
It includes a handler class `StaticConditionalHandler` to manage the conditions and evaluate them.
"""

from typing import List, Dict, Union
from kenkenpa.common import convert_key

def add_static_conditional_edge(metadata,settings,evaluate_functions):
    """
    Adds a static conditional edge based on the provided settings and evaluation functions.

    Args:
        metadata: Metadata information (not used in the current implementation).
        settings (dict): A dictionary containing the conditions for the static conditional edge.
        evaluate_functions (dict): A dictionary of functions used to evaluate conditions.

    Returns:
        function: A function that evaluates the conditions and returns
        the result based on the state and config.
    """
    conditions = metadata['flow_parameter']['conditions']

    conditional_edge = StaticConditionalHandler(conditions,evaluate_functions)

    return conditional_edge.call_edge

class StaticConditionalHandler:
    """
    A handler class to manage and evaluate static conditional edges based on given
    conditions and evaluation functions.

    Attributes:
        conditions (list): A list of conditions to evaluate.
        evaluate_functions (dict): A dictionary of functions used to evaluate conditions.
        end_points (list): A list of possible end points extracted from the conditions.
    """
    def __init__(self,conditions,evaluate_functions):
        """
        Initializes the StaticConditionalHandler with conditions and evaluation functions.

        Args:
            conditions (list): A list of conditions to evaluate.
            evaluate_functions (dict): A dictionary of functions used to evaluate conditions.
        """
        self.conditions = conditions
        self.evaluate_functions = evaluate_functions

    def call_edge(self, state,config):
        """
        Evaluates the conditions based on the given state and config, and returns the result.

        Args:
            state (dict): The current state to evaluate.
            config (dict): The configuration to use during evaluation.

        Returns:
            str: The result of the evaluated condition.
        """
        result = self.evaluate_conditions(state, self.conditions, config)

        return convert_key(result)

    def evaluate_conditions(self, state, conditions, config):
        """
        Evaluates the conditions based on the given state and config, and returns the result.

        Args:
            state (dict): The current state to evaluate.
            conditions (list): A list of conditions to evaluate.
            config (dict): The configuration to use during evaluation.

        Returns:
            str: The result of the evaluated condition.

        Raises:
            ValueError: If no matching condition is found and no default function is provided.
        """
        for condition in conditions:
            if "expression" in condition and self.evaluate_expr(
                state, condition["expression"], config
                ):
                return condition["result"]
        # どの条件も一致しない場合、デフォルトの関数を返す
        for condition in conditions:
            if "default" in condition:
                return condition["default"]
        raise ValueError("一致する条件が見つからず、デフォルト関数が提供されていません")

    def evaluate_expr(self,state, expr, config):
        """
        Evaluates a single expression based on the given state and config.

        Args:
            state (dict): The current state to evaluate.
            expr (dict): The expression to evaluate.
            config (dict): The configuration to use during evaluation.

        Returns:
            bool: The result of the evaluated expression.

        Raises:
            ValueError: If the expression is not a dictionary or
            contains unsupported types or operations.
        """
        if not isinstance(expr, dict):
            raise ValueError("式は辞書である必要があります")

        def get_value(item):
            if isinstance(item, dict):
                if item["type"] == "state_value":
                    return state.get(item["name"])
                elif item["type"] == "function":
                    func_name = item["name"]
                    if func_name not in self.evaluate_functions:
                        raise ValueError(f"関数 {func_name} が evaluate_functions に見つかりません")
                    args = item.get("args", {})
                    return self.evaluate_functions[func_name](state, config, **args)
                else:
                    raise ValueError(f"サポートされていないタイプ: {item['type']}")
            else:
                return item  # スカラー値

        for op, args in expr.items():
            if op == "and":
                return all(self.evaluate_expr(state, sub_expr,  config) for sub_expr in args)
            elif op == "or":
                return any(self.evaluate_expr(state, sub_expr,  config) for sub_expr in args)
            elif op == "not":
                return not self.evaluate_expr(state, args,  config)
            elif op in {"==", "!=", ">", ">=", "<", "<=",
                        "equals","not_equals","greater_than","greater_than_or_equals",
                        "less_than","less_than_or_equals",
                        "eq","neq","gt","gte","lt","lte",
                        }:
                left_item, right_item = args
                left_value = get_value(left_item)
                right_value = get_value(right_item)
                return compare_values(op,left_value,right_value)
            else:
                raise ValueError(f"サポートされていない演算: {op}")
            

def compare_values(op,left_value,right_value):
    comparison_operations = {
        "==": lambda x, y: x == y,
        "equals": lambda x, y: x == y,
        "eq": lambda x, y: x == y,
        "!=": lambda x, y: x != y,
        "not_equals": lambda x, y: x != y,
        "neq": lambda x, y: x != y,
        ">": lambda x, y: x > y,
        "greater_than": lambda x, y: x > y,
        "gt": lambda x, y: x > y,
        ">=": lambda x, y: x >= y,
        "greater_than_or_equals": lambda x, y: x >= y,
        "gte": lambda x, y: x >= y,
        "<": lambda x, y: x < y,
        "less_than": lambda x, y: x < y,
        "lt": lambda x, y: x < y,
        "<=": lambda x, y: x <= y,
        "less_than_or_equals": lambda x, y: x <= y,
        "lte": lambda x, y: x <= y
    }
    if op in comparison_operations:
        return comparison_operations[op](left_value,right_value)
    else:
        raise ValueError(f"サポートされていない比較演算子: {op}")