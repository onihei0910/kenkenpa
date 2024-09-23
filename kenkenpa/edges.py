"""
This module provides functionality for generating and handling static conditional edges.
It includes a function to generate a static conditional edge and a class to handle the evaluation of conditions.
"""
from kenkenpa.common import to_list_key

def gen_static_conditional_edge(conditions,evaluate_functions):
    """
    Generates a static conditional edge based on the provided conditions and evaluation functions.

    Args:
        conditions (List[Dict]): A list of conditions for the edge.
        evaluate_functions (Dict[str, callable]): A dictionary of evaluation functions.

    Returns:
        callable: The function to call for the edge.
    """
    conditional_edge = StaticConditionalHandler(conditions,evaluate_functions)

    return conditional_edge.call_edge

class StaticConditionalHandler:
    """
    StaticConditionalHandler evaluates conditions and returns results based on the state and configuration.

    Attributes:
        conditions (List[Dict]): A list of conditions to evaluate.
        evaluate_functions (Dict[str, callable]): A dictionary of evaluation functions.
    """
    def __init__(self,conditions,evaluate_functions):
        """
        Initializes the StaticConditionalHandler with conditions and evaluation functions.

        Args:
            conditions (List[Dict]): A list of conditions to evaluate.
            evaluate_functions (Dict[str, callable]): A dictionary of evaluation functions.
        """
        self.conditions = conditions
        self.evaluate_functions = evaluate_functions

    def call_edge(self, state,config):
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
        results = []
        for condition in conditions:
            if "expression" in condition and self._evaluate_expr(
                condition["expression"], state, config
                ):
                
                results.extend(to_list_key(condition["result"]))
        if results:
            return results

        # どの条件も一致しない場合、デフォルトの関数を返す
        for condition in conditions:
            if "default" in condition:
                results.extend(to_list_key(condition["default"]))
        
        if results:
            return results
            
        raise ValueError("一致する条件が見つからず、デフォルト関数が提供されていません")

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
            raise ValueError("式は辞書である必要があります")

        def get_value(item):
            if isinstance(item, dict):
                if item["type"] == "state_value":
                    return state.get(item["name"])
                elif item["type"] == "config_value":
                    return config.get("configurable",{}).get(item["name"]) # TODO これはlanggraphに合わせる必要あり。app.stream(inputs, {"configurable": {"user_id": "123"}})
                elif item["type"] == "function":
                    func_name = item["name"]
                    if func_name not in self.evaluate_functions:
                        raise ValueError(f"関数 {func_name} が evaluate_functions に見つかりません")
                    args = item.get("args", {})
                    return self.evaluate_functions[func_name](state, config, **args)
                else:
                    raise ValueError(f"サポートされていないタイプ: {item['type']}")
            else:
                return item

        for op, args in expr.items():
            if op == "and":
                return all(self._evaluate_expr(sub_expr, state, config) for sub_expr in args)
            elif op == "or":
                return any(self._evaluate_expr(sub_expr, state, config) for sub_expr in args)
            elif op == "not":
                return not self._evaluate_expr(args, state, config)
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