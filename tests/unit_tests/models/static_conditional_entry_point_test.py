import pytest
from kenkenpa.models.static_conditional_entry_point import KConditionalEntoryPointFlowParam_v1
from kenkenpa.models.static_conditional_entry_point import KConditionalEntoryPointFlowParam

from kenkenpa.models.static_conditional_entry_point import KStaticConditionalEntoryPoint_v1
from kenkenpa.models.static_conditional_entry_point import KStaticConditionalEntoryPoint

def test_KConditionalEdgeFlowParam():
    flow_parameter = {
            "path_map":["generate_joke"],
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

    KConditionalEntoryPointFlowParam_v1(**flow_parameter)
    KConditionalEntoryPointFlowParam(**flow_parameter)

    flow_parameter = {
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

    KConditionalEntoryPointFlowParam_v1(**flow_parameter)
    KConditionalEntoryPointFlowParam(**flow_parameter)

def test_KStaticConditionalEdge():
    flow = {
            "graph_type":"static_conditional_entry_point",
            "flow_parameter":{
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
    
    KStaticConditionalEntoryPoint_v1(**flow)
    KStaticConditionalEntoryPoint(**flow)