"""
This module provides functionality for generating and
handling configurable conditional edges.
It includes a function to generate a configurable conditional edge and
a class to handle the evaluation of conditions.
"""
from typing import List
from kenkenpa.common import convert_key

class ConfigurableConditionalHandler:
    """
    ConfigurableConditionalHandler evaluates conditions and
    returns results based on the state and configuration.

    Attributes:
        conditions (List[Dict]): A list of conditions to evaluate.
        evaluate_functions (Dict[str, callable]): A dictionary of evaluation functions.
    """
    def __init__(self,conditions,evaluate_functions):
        """
        Initializes the ConfigurableConditionalHandler with conditions and evaluation functions.

        Args:
            conditions (List[Dict]): A list of conditions to evaluate.
            evaluate_functions (Dict[str, callable]): A dictionary of evaluation functions.
        """
        self.conditions = conditions
        self.evaluate_functions = evaluate_functions

    def __call__(self, state,config):
        """
        Calls the edge based on the current state and configuration.

        Args:
            state (Dict): The current state.
            config (Dict): The configuration.

        Returns:
            List: The results of the evaluated conditions.
        """
        results = self._evaluate_conditions(self.conditions, state, config)
        return results

    def _evaluate_conditions(self, conditions, state, config):
        """
        Evaluates the conditions and returns the results.

        Args:
            conditions (List[Dict]): The conditions to evaluate.
            state (Dict): The current state.
            config (Dict): The configuration.

        Returns:
            List: The results of the evaluated conditions.

        Raises:
            ValueError: If no matching conditions are found and no default function is provided.
        """
        results = self._evaluate_matching_conditions(conditions, state, config)
        if results:
            return results

        results = self._evaluate_default_conditions(conditions, state, config)
        if results:
            return results

        raise ValueError("No matching conditions were found, and no default function was provided.")

    def _evaluate_matching_conditions(self, conditions, state, config):
        """
        Evaluates the conditions that match the given state and config.

        Args:
            conditions (List[Dict]): The conditions to evaluate.
            state (Dict): The current state.
            config (Dict): The configuration.

        Returns:
            List: The results of the evaluated conditions.
        """
        results = []
        for condition in conditions:
            if ("expression" in condition and
                self._evaluate_expr(condition["expression"], state, config)):
                results.extend(self._process_result(condition["result"], state, config))
        return results

    def _evaluate_default_conditions(self, conditions, state, config):
        """
        Evaluates the default conditions if no matching conditions are found.

        Args:
            conditions (List[Dict]): The conditions to evaluate.
            state (Dict): The current state.
            config (Dict): The configuration.

        Returns:
            List: The results of the evaluated conditions.
        """
        results = []
        for condition in conditions:
            if "default" in condition:
                results.extend(self._process_result(condition["default"], state, config))
        return results

    def _process_result(self, result, state, config):
        """
        Processes the result value and converts keys if necessary.

        Args:
            result: The result value to process.
            state (Dict): The current state.
            config (Dict): The configuration.

        Returns:
            List: The processed result values.
        """
        result_value = self._get_value(result, state, config)
        if isinstance(result_value, List):
            return [convert_key(wk) if isinstance(wk, str) else wk for wk in result_value]

        return [convert_key(result_value) if isinstance(result_value, str) else result_value]

    def _evaluate_expr(self,expr, state, config):
        """
        Evaluates an expression against the current state and configuration.

        Args:
            expr (Dict): The expression to evaluate.
            state (Dict): The current state.
            config (Dict): The configuration.

        Returns:
            bool: The result of the evaluation.

        Raises:
            ValueError: If the expression is not a dictionary.
        """
        if not isinstance(expr, dict):
            raise ValueError("The formula must be a dictionary.")

        for op, args in expr.items():
            if op == "and":
                return all(self._evaluate_expr(sub_expr, state, config) for sub_expr in args)
            if op == "or":
                return any(self._evaluate_expr(sub_expr, state, config) for sub_expr in args)
            if op == "not":
                return not self._evaluate_expr(args, state, config)
            if op in {"==", "!=", ">", ">=", "<", "<=",
                        "equals","not_equals","greater_than","greater_than_or_equals",
                        "less_than","less_than_or_equals",
                        "eq","neq","gt","gte","lt","lte",
                        }:
                left_item, right_item = args
                left_value = self._get_value(left_item,state, config)
                right_value = self._get_value(right_item,state, config)
                return compare_values(op,left_value,right_value)

            raise ValueError(f"Unsupported operation: {op}")

    def _get_value(self,item, state, config):
        if isinstance(item, dict):
            if item["type"] == "state_value":
                return state.get(item["name"])
            if item["type"] == "config_value":
                return config.get("configurable",{}).get(item["name"])
            if item["type"] == "function":
                func_name = item["name"]
                if func_name not in self.evaluate_functions:
                    raise ValueError(
                        f"The function {func_name} cannot be found in evaluate_functions."
                        )
                args = item.get("args", {})
                return self.evaluate_functions[func_name](state, config, **args)

            raise ValueError(f"Unsupported type: {item['type']}")

        return item

def compare_values(op,left_value,right_value):
    """
    Compares two values based on the specified operator.

    Parameters:
    op (str): The comparison operator (e.g., '==', '>', '<=', etc.).
    left_value: The left value to compare.
    right_value: The right value to compare.

    Returns:
    bool: The result of the comparison.

    Raises:
    ValueError: If the operator is unsupported.
    """
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

    raise ValueError(f"Unsupported comparison operator: {op}")
