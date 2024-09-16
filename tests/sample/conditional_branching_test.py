"""
このテストは、LangGraphの"Parallel node fan-out and fan-in"を例にkenkenpaの使用方法を説明します。
https://langchain-ai.github.io/langgraph/how-tos/branching/
"""

import operator
from typing import Any
from langchain_core.pydantic_v1 import BaseModel

from kenkenpa.builder import WorkFlowBuilder

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

# ReturnNodeValueを返すジェネレーター関数を定義します。
def gen_return_node_value(generator_parameter,flow_parameter):

    class ReturnNodeValue:
        def __init__(self, node_secret: str):
            self._value = node_secret

        def __call__(self, state ) -> Any:
            print(f"Adding {self._value} to {state['aggregate']}")
            return {"aggregate": [self._value]}
    
    object = ReturnNodeValue(generator_parameter['node_secret'])
    return object

# コンパイル可能なStateGraphの設定を辞書形式で記述します。
graph_settings = {
    "workflow_type":"workflow",
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
            "workflow_type":"node",
            "flow_parameter": {
                "name":"a",
                "generator":"gen_return_node_value", 
            },
            "generator_parameter" : {"node_secret":"I'm A"},
        },
        { # normal_edge START-> a
            "workflow_type":"edge",
            "flow_parameter":{
                "start_key":"START",
                "end_key":"a"
            },
        },
        { # node b
            "workflow_type":"node",
            "flow_parameter": {
                "name":"b",
                "generator":"gen_return_node_value", 
            },
            "generator_parameter" : {"node_secret":"I'm B"},
        },
        { # node c
            "workflow_type":"node",
            "flow_parameter": {
                "name":"c",
                "generator":"gen_return_node_value", 
            },
            "generator_parameter" : {"node_secret":"I'm C"},
        },
        { # node d
            "workflow_type":"node",
            "flow_parameter": {
                "name":"d",
                "generator":"gen_return_node_value", 
            },
            "generator_parameter" : {"node_secret":"I'm D"},
        },
        { # node e
            "workflow_type":"node",
            "flow_parameter": {
                "name":"e",
                "generator":"gen_return_node_value", 
            },
            "generator_parameter" : {"node_secret":"I'm E"},
        },
        { # 静的条件付きエッジ a -> b,c or c,d
            "workflow_type":"conditional_edge",
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
            "workflow_type":"edge",
            "flow_parameter": {
                "start_key":["b","c","d"],
                "end_key":"e"
            },
        },
        { # normal_edge e -> END
            "workflow_type":"edge",
            "flow_parameter": {
                "start_key":"e",
                "end_key":"END"
            },
        },
    ]
}

class ConfigSchema(BaseModel): #pylint:disable=too-few-public-methods
    dummy : str = "dummy config"

def test_conditional_branching():

    # graph_settingsからWorkFlowBuilderを生成します。
    workflow_builder = WorkFlowBuilder(graph_settings,ConfigSchema) # TODO Configは任意項目にする

    #listは基本型として予約されてます。(*1)
    #workflow_builder.add_type("list",list)  # Error

    # Stateで使用するreducerをマッピングします。
    workflow_builder.add_reducer("add",operator.add)

    # workflow_builderにノードジェネレーターを登録しておきます。
    workflow_builder.add_node_generator("gen_return_node_value",gen_return_node_value)

    # getworkflowメソッドでコンパイル可能なStateGraphを取得できます。
    workflow = workflow_builder.getworkflow()

    graph = workflow.compile() 

    print(f"\ngraph")
    graph.get_graph().print_ascii()

    print('graph.invoke({"aggregate": [],"which":"bc"}, {"configurable": {"thread_id": "foo"}})')
    graph.invoke({"aggregate": [],"which":"bc"}, {"configurable": {"thread_id": "foo"}})

    print('graph.invoke({"aggregate": [],"which":"cd"}, {"configurable": {"thread_id": "foo"}})')
    graph.invoke({"aggregate": [],"which":"cd"}, {"configurable": {"thread_id": "foo"}})
    # WorkFlowBuilderでは以下の型が基本型として事前に登録されています。
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