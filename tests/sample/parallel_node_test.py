"""
このテストは、LangGraphの"Parallel node fan-out and fan-in"を例にkenkenpaの使用方法を説明します。
https://langchain-ai.github.io/langgraph/how-tos/branching/
"""

import operator
from typing import Any
from langchain_core.pydantic_v1 import BaseModel

from kenkenpa.builder import WorkFlowBuilder

# Stateは定義しません。graph_settingsの中で定義します。
# class State(TypedDict):
    # The operator.add reducer fn makes this append-only
    # aggregate: Annotated[list, operator.add]

# ReturnNodeValueを返すジェネレーター関数を定義します。
def gen_return_node_value(metadata,settings):

    class ReturnNodeValue:
        def __init__(self, node_secret: str):
            self._value = node_secret

        def __call__(self, state ) -> Any:
            print(f"Adding {self._value} to {state['aggregate']}")
            return {"aggregate": [self._value]}
    
    object = ReturnNodeValue(settings['node_secret'])
    
    # graph_settingsの中で、以下のようにジェネレーター関数に渡すデータを定義できます。
    #{ 
    #    "metadata" : {
    #        "workflow_type":"node",
    #        "flow_parameter": {
    #            "name":"a",
    #            "generator":"gen_return_node_value", 
    #        }
    #    },
    #    "settings" : {"node_secret":"I'm A"}, 
    # ,

    #return object.__call__ # TODO オブジェクトごと返すパターン。
    return object

# コンパイル可能なStateGraphの設定を辞書形式で記述します。
graph_settings = {
    "metadata":{
        "workflow_type":"workflow",
        "flow_parameter":{
            "name":"Parallel-node",
        }
    },
    # state"aggregate"はここで設定します。
    "state" : [ 
        {
            "field_name": "aggregate", #フィールド名
            "type": "list", # 型
            "reducer":"add" # reducerと紐づけるキー
        },
    ],
    "flows": [
        { # node A
            "metadata" : {
                "workflow_type":"node",
                "flow_parameter": {
                    "name":"a",
                    "generator":"gen_return_node_value", 
                }
            },
            "settings" : {"node_secret":"I'm A"}, # TODO settingsが無い場合は設定しなくてもよい。(optional)
        },
        { # normal_edge START-> a
            "metadata" :{
                "workflow_type":"edge",
                "flow_parameter":{
                    "start_key":"START",
                    "end_key":"a"
                }
            },
        },
        { # node b
            "metadata" : {
                "workflow_type":"node",
                "flow_parameter": {
                    "name":"b",
                    "generator":"gen_return_node_value", 
                }
            },
            "settings" : {"node_secret":"I'm B"}, # TODO settingsが無い場合は設定しなくてもよい。(optional)
        },
        { # node c
            "metadata" : {
                "workflow_type":"node",
                "flow_parameter": {
                    "name":"c",
                    "generator":"gen_return_node_value", 
                }
            },
            "settings" : {"node_secret":"I'm C"}, # TODO settingsが無い場合は設定しなくてもよい。(optional)
        },
        { # node d
            "metadata" : {
                "workflow_type":"node",
                "flow_parameter": {
                    "name":"d",
                    "generator":"gen_return_node_value", 
                }
            },
            "settings" : {"node_secret":"I'm D"}, # TODO settingsが無い場合は設定しなくてもよい。(optional)
        },
        { # normal_edge a -> b
            "metadata" :{
                "workflow_type":"edge",
                "flow_parameter": {
                    "start_key":"a",
                    "end_key":"b"
                }
            },
        },
        { # normal_edge a -> c
            "metadata" :{
                "workflow_type":"edge",
                "flow_parameter": {
                    "start_key":"a",
                    "end_key":"c"
                }
            },
        },
        { # normal_edge b -> d
            "metadata" :{
                "workflow_type":"edge",
                "flow_parameter": {
                    "start_key":"b",
                    "end_key":"d"
                }
            },
        },
        { # normal_edge c -> d
            "metadata" :{
                "workflow_type":"edge",
                "flow_parameter": {
                    "start_key":"c",
                    "end_key":"d"
                }
            },
        },
        { # normal_edge d -> END
            "metadata" :{
                "workflow_type":"edge",
                "flow_parameter": {
                    "start_key":"d",
                    "end_key":"END"
                }
            },
        },
    ]
}

class ConfigSchema(BaseModel): #pylint:disable=too-few-public-methods
    dummy : str = "dummy config"


def test_parallel_node():

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
    graph.get_graph().print_ascii()

    graph.invoke({"aggregate": []}, {"configurable": {"thread_id": "foo"}})

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