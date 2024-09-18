"""
このテストは、LangGraphの"Parallel node fan-out and fan-in"を例にkenkenpaの使用方法を説明します。
https://langchain-ai.github.io/langgraph/how-tos/branching/
"""

import operator
from typing import Any

from kenkenpa.builder import StateGraphBuilder

# Stateは定義しません。graph_settingsの中で定義します。
#class State(TypedDict):
    # The operator.add reducer fn makes this append-only
    # aggregate: Annotated[list, operator.add]
    # which: str

# stateを参照するconditional edgeはgraph_settingsの中で定義するため、これも定義しません。
#def route_bc_or_cd(state: State) -> Sequence[str]:
    #if state["which"] == "cd":
    #    return ["c", "d"]
    #return ["b", "c"]

# ReturnNodeValueを返すファクトリー関数を定義します。
def gen_return_node_value(factory_parameter,flow_parameter):

    class ReturnNodeValue:
        def __init__(self, node_secret: str):
            self._value = node_secret

        def __call__(self, state ) -> Any:
            print(f"Adding {self._value} to {state['aggregate']}")
            return {"aggregate": [self._value]}
    
    object = ReturnNodeValue(factory_parameter['node_secret'])
    return object

# コンパイル可能なStateGraphの設定を辞書形式で記述します。
graph_settings = {
    "graph_type":"stategraph",
    "flow_parameter":{
        "name":"Parallel-node",
        "state" : [ 
            {
                "field_name": "aggregate", #フィールド名
                "type": "list", # 型
                "reducer":"add" # reducerと紐づけるキー
            },
            {
                "field_name": "which", #フィールド名
                "type": "str", # 型
            },
        ],
    },
    "flows": [
        { # node a
            "graph_type":"node",
            "flow_parameter": {
                "name":"a",
                "factory":"gen_return_node_value", 
            },
            "factory_parameter" : {"node_secret":"I'm A"},
        },
        { # normal_edge START-> a
            "graph_type":"edge",
            "flow_parameter":{
                "start_key":"START",
                "end_key":"a"
            },
        },
        { # node b
            "graph_type":"node",
            "flow_parameter": {
                "name":"b",
                "factory":"gen_return_node_value", 
            },
            "factory_parameter" : {"node_secret":"I'm B"},
        },
        { # node c
            "graph_type":"node",
            "flow_parameter": {
                "name":"c",
                "factory":"gen_return_node_value", 
            },
            "factory_parameter" : {"node_secret":"I'm C"},
        },
        { # node d
            "graph_type":"node",
            "flow_parameter": {
                "name":"d",
                "factory":"gen_return_node_value", 
            },
            "factory_parameter" : {"node_secret":"I'm D"},
        },
        { # node e
            "graph_type":"node",
            "flow_parameter": {
                "name":"e",
                "factory":"gen_return_node_value", 
            },
            "factory_parameter" : {"node_secret":"I'm E"},
        },
        { # 静的条件付きエッジ a -> b,c or c,d
            "graph_type":"static_conditional_edge",
            "flow_parameter":{
                "start_key":"a",
                "conditions":[
                    {
                        "expression": {
                            "eq": [{"type": "state_value", "name": "which"}, "cd"],
                        },
                        "result": ["c","d"]
                    },
                    {"default": ["b","c"]} 
                ]
            },
        },
        { # normal_edge b,c,d -> e
            "graph_type":"edge",
            "flow_parameter": {
                "start_key":["b","c","d"],
                "end_key":"e"
            },
        },
        { # normal_edge e -> END
            "graph_type":"edge",
            "flow_parameter": {
                "start_key":"e",
                "end_key":"END"
            },
        },
    ]
}

def test_conditional_branching():

    # graph_settingsからStateGraphBuilderを生成します。
    stategraph_builder = StateGraphBuilder(graph_settings)

    #listは基本型として予約されてます。(*1)
    #stategraph_builder.add_type("list",list)  # Error

    # Stateで使用するreducerをマッピングします。
    stategraph_builder.add_reducer("add",operator.add)

    # stategraph_builderにノードファクトリーを登録しておきます。
    stategraph_builder.add_node_factory("gen_return_node_value",gen_return_node_value)

    # gen_stategraphメソッドでコンパイル可能なStateGraphを取得できます。
    stategraph = stategraph_builder.gen_stategraph()

    graph = stategraph.compile() 

    print(f"\ngraph")
    graph.get_graph().print_ascii()

    print('graph.invoke({"aggregate": [],"which":"bc"}, {"configurable": {"thread_id": "foo"}})')
    graph.invoke({"aggregate": [],"which":"bc"}, {"configurable": {"thread_id": "foo"}})

    print('graph.invoke({"aggregate": [],"which":"cd"}, {"configurable": {"thread_id": "foo"}})')
    graph.invoke({"aggregate": [],"which":"cd"}, {"configurable": {"thread_id": "foo"}})
    # StateGraphBuilderでは以下の型が基本型として事前に登録されています。
    # "int":int,
    # "float":float,
    # "complex":complex,
    # "str":str,
    # "list":list,
    # "tuple":tuple,
    # "dict":dict,
    # "set":set,
    # "frozenset":frozenset,
    # "bool":bool,