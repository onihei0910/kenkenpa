import pytest
from kenkenpa.models.static_conditional_edge import KConditionalEdgeFlowParam_v1
from kenkenpa.models.static_conditional_edge import KConditionalEdgeFlowParam

from kenkenpa.models.static_conditional_edge import KStaticConditionalEdge_v1
from kenkenpa.models.static_conditional_edge import KStaticConditionalEdge

def test_KConditionalEdgeFlowParam():
    flow_parameter = {
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
        }

    KConditionalEdgeFlowParam_v1(**flow_parameter)
    KConditionalEdgeFlowParam(**flow_parameter)

def test_StaticConditionalEdge():
    flow = {
            "graph_type":"static_conditional_edge",
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
    
    KStaticConditionalEdge_v1(**flow)
    KStaticConditionalEdge(**flow)