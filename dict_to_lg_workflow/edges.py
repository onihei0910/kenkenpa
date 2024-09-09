from typing import List, Dict, Union

def add_static_conditional_edge(metadata,settings,evaluate_functions):
    # edgesの抽出
    conditions = settings['conditions']

    conditional_edge = StaticConditionalHandler(conditions,evaluate_functions)

    # call_edgeの戻り値の型を設定
    call_edge_return_type = conditional_edge.get_call_edge_return_type()
    conditional_edge.call_edge.__annotations__['return'] = call_edge_return_type

    return conditional_edge.call_edge

class StaticConditionalHandler:
    def __init__(self,conditions,evaluate_functions):
        self.conditions = conditions
        self.evaluate_functions = evaluate_functions
        self.end_points = self._extract_literals(self.conditions)

    def call_edge(self, state,config):
        result = self.evaluate_conditions(state, self.conditions, config)

        return result

    def _extract_literals(self, conditions: List[Dict[str, Union[Dict, str]]]) -> str:
        results = []
        for condition in conditions:
            if 'result' in condition:
                results.append(condition['result'])
            elif 'default' in condition:
                results.append(condition['default'])
        return results

    def get_call_edge_return_type(self):
        literal_type_str = f"Literal[{', '.join([f'\"{result}\"' for result in self.end_points])}]"
        return eval(literal_type_str)

    def evaluate_conditions(self, state, conditions, config):
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
