import pytest

from kenkenpa.models.stategraph import KState_v1
from kenkenpa.models.stategraph import KState

from kenkenpa.models.stategraph import KStateGraphParam_v1
from kenkenpa.models.stategraph import KStateGraphParam

from kenkenpa.models.stategraph import KStateGraph_v1
from kenkenpa.models.stategraph import KStateGraph

def test_KState():
    state = {
            "field_name": "aggregate",
            "type": "list",
            "reducer":"add"
        }

    KState_v1(**state)
    KState(**state)

    state = {
            "field_name": "which",
            "type": "str",
        }

    KState_v1(**state)
    KState(**state)

def test_KStateGraphParam():
    flow_parameter = {
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
    }

    KStateGraphParam_v1(**flow_parameter)
    KStateGraphParam(**flow_parameter)

    flow_parameter = {
        "name":"Parallel-node"
    }

    KStateGraphParam_v1(**flow_parameter)
    KStateGraphParam(**flow_parameter)

def test_KStateGraph():
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
            { # 静的条件付きエッジ __start__ -> b,c or c,d
                "graph_type":"static_conditional_entry_point",
                "flow_parameter":{
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

    KStateGraph_v1(**graph_settings)
    KStateGraph(**graph_settings)
