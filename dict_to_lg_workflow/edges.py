"""
This module provides functionality to add static conditional edges based on given
conditions and evaluation functions.
It includes a handler class `StaticConditionalHandler` to manage the conditions and evaluate them.
"""

from typing import List, Dict, Union, Literal
from langgraph.graph import START,END

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
    # edgesの抽出
    conditions = settings['conditions']

    conditional_edge = StaticConditionalHandler(conditions,evaluate_functions)

    # call_edgeの戻り値の型を設定
    call_edge_return_type = conditional_edge.get_call_edge_return_type()
    conditional_edge.call_edge.__annotations__['return'] = call_edge_return_type

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
        self.end_points = self._extract_literals(self.conditions)

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

        # TODO リファクタリング "END"をENDに変換する処理を最適化
        print(f"result:{result}")
        if result == "END":
            return END

        return result

    def _extract_literals(self, conditions: List[Dict[str, Union[Dict, str]]]) -> str:
        """
        Extracts literal values from the conditions.

        Args:
            conditions (list): A list of conditions to extract literals from.

        Returns:
            list: A list of literal values extracted from the conditions.
        """
        results = []
        for condition in conditions:
            if 'result' in condition:
                results.append(condition['result'])
            elif 'default' in condition:
                results.append(condition['default'])
        return results

    def get_call_edge_return_type(self):
        """
        Constructs and returns the return type for the call_edge method based on
        the extracted literals.

        Returns:
            type: The return type for the call_edge method.
        """
        # TODO リファクタリング "END"をENDに変換する処理を最適化
        literal_type_str_oridinal = f"Literal[{', '.join([f'\"{result}\"' for result in self.end_points])}]"
        print(f"literal_type_str_oridinal:{literal_type_str_oridinal}")
        literal_type_str = literal_type_str_oridinal.replace('\"END\"', 'END')
        print(f"literal_type_str:{literal_type_str}")
        return eval(literal_type_str)

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
            elif op in {"==", "!=", ">", ">=", "<", "<="}:
                left_item, right_item = args
                left_value = get_value(left_item)
                right_value = get_value(right_item)
                if op == "==":
                    return left_value == right_value
                elif op == "!=":
                    return left_value != right_value
                elif op == ">":
                    return left_value > right_value
                elif op == ">=":
                    return left_value >= right_value
                elif op == "<":
                    return left_value < right_value
                elif op == "<=":
                    return left_value <= right_value
            else:
                raise ValueError(f"サポートされていない演算: {op}")
