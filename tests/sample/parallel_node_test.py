"""
このテストは、LangGraphの"Conditional Branching"を例にkenkenpaの使用方法を説明します。
https://langchain-ai.github.io/langgraph/how-tos/branching/#conditional-branching
"""

import operator
from typing import Any

from kenkenpa.builder import StateGraphBuilder

# Stateは定義しません。graph_settingsの中で定義します。
# class State(TypedDict):
    # The operator.add reducer fn makes this append-only
    # aggregate: Annotated[list, operator.add]

# ReturnNodeValueを返すジェネレーター関数を定義します。
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
        # state"aggregate"はここで設定します。
        "state" : [ 
            {
                "field_name": "aggregate", #フィールド名
                "type": "list", # 型
                "reducer":"add" # reducerと紐づけるキー
            },
        ],
    },
    "flows": [
        { # node A
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
        { # normal_edge a -> b,c
            "graph_type":"edge",
            "flow_parameter": {
                "start_key":"a",
                "end_key":["b","c"],
            },
        },
        { # normal_edge b,c -> d
            "graph_type":"edge",
            "flow_parameter": {
                "start_key":["b","c"],
                "end_key":"d"
            },
        },
        { # normal_edge d -> END
            "graph_type":"edge",
            "flow_parameter": {
                "start_key":"d",
                "end_key":"END"
            },
        },
    ]
}

def test_parallel_node():

    # graph_settingsからStateGraphBuilderを生成します。
    stategraph_builder = StateGraphBuilder(graph_settings)

    #listは基本型として予約されてます。(*1)
    #stategraph_builder.add_type("list",list)  # Error

    # Stateで使用するreducerをマッピングします。
    stategraph_builder.add_reducer("add",operator.add)

    # stategraph_builderにノードジェネレーターを登録しておきます。
    stategraph_builder.add_node_factory("gen_return_node_value",gen_return_node_value)

    # gen_stategraphメソッドでコンパイル可能なStateGraphを取得できます。
    stategraph = stategraph_builder.gen_stategraph()

    graph = stategraph.compile() 

    print(f"\ngraph")
    graph.get_graph().print_ascii()

    graph.invoke({"aggregate": []}, {"configurable": {"thread_id": "foo"}})

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