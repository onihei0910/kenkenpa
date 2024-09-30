import pytest

from kenkenpa.models.stategraph import KStateV1
from kenkenpa.models.stategraph import KState

from kenkenpa.models.stategraph import KStateGraphParamV1
from kenkenpa.models.stategraph import KStateGraphParam

from kenkenpa.models.stategraph import KStateGraphV1
from kenkenpa.models.stategraph import KStateGraph

def test_KState():
    state = {
            "field_name": "aggregate",
            "type": "list",
            "reducer":"add"
        }

    KStateV1(**state)
    KState(**state)

    state = {
            "field_name": "which",
            "type": "str",
        }

    KStateV1(**state)
    KState(**state)

def test_KStateGraphParam():
    flow_parameter = {
        "name":"Parallel-node",
        "state" : [ 
            {
                "field_name": "aggregate",
                "type": "list",
                "reducer":"add"
            },
            {
                "field_name": "which",
                "type": "str",
            },
        ],
    }

    KStateGraphParamV1(**flow_parameter)
    KStateGraphParam(**flow_parameter)

    flow_parameter = {
        "name":"Parallel-node"
    }

    KStateGraphParamV1(**flow_parameter)
    KStateGraphParam(**flow_parameter)

def test_KStateGraph():
    graph_settings = {
        "graph_type":"stategraph",
        "flow_parameter":{
            "name":"Parallel-node",
            "state" : [ 
                {
                    "field_name": "aggregate",
                    "type": "list",
                    "reducer":"add"
                },
                {
                    "field_name": "which",
                    "type": "str",
                },
            ],
        },
        "flows": [
            {
                "graph_type":"configurable_conditional_entry_point",
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
            {
                "graph_type":"node",
                "flow_parameter": {
                    "name":"b",
                    "factory":"gen_return_node_value", 
                },
                "factory_parameter" : {"node_secret":"I'm B"},
            },
            {
                "graph_type":"node",
                "flow_parameter": {
                    "name":"c",
                    "factory":"gen_return_node_value", 
                },
                "factory_parameter" : {"node_secret":"I'm C"},
            },
            {
                "graph_type":"node",
                "flow_parameter": {
                    "name":"d",
                    "factory":"gen_return_node_value", 
                },
                "factory_parameter" : {"node_secret":"I'm D"},
            },
            {
                "graph_type":"node",
                "flow_parameter": {
                    "name":"e",
                    "factory":"gen_return_node_value", 
                },
                "factory_parameter" : {"node_secret":"I'm E"},
            },

            {
                "graph_type":"edge",
                "flow_parameter": {
                    "start_key":["b","c","d"],
                    "end_key":"e"
                },
            },
            {
                "graph_type":"edge",
                "flow_parameter": {
                    "start_key":"e",
                    "end_key":"END"
                },
            },
            {
                "graph_type":"configurable_conditional_edge",
                "flow_parameter":{
                    "start_key":"agent",
                    "conditions":[
                        {
                            "expression": {
                                "eq": [
                                    {"type": "function", "name": "is_tool_message_function"},
                                    True
                                    ],
                            },
                            "result": "tools"
                        },
                        {"default": "END"} 
                    ]
                },
            }
        ]
    }

    KStateGraphV1(**graph_settings)
    KStateGraph(**graph_settings)
