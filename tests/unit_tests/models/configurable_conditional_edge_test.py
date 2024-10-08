import pytest
from kenkenpa.models.configurable_conditional_edge import KConditionalEdgeFlowParamV1
from kenkenpa.models.configurable_conditional_edge import KConditionalEdgeFlowParam

from kenkenpa.models.configurable_conditional_edge import KConfigurableConditionalEdgeV1
from kenkenpa.models.configurable_conditional_edge import KConfigurableConditionalEdge

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

    KConditionalEdgeFlowParamV1(**flow_parameter)
    KConditionalEdgeFlowParam(**flow_parameter)

    flow_parameter = {
            "start_key":"agent",
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

    KConditionalEdgeFlowParamV1(**flow_parameter)
    KConditionalEdgeFlowParam(**flow_parameter)

def test_ConfigurableConditionalEdge():
    flow = {
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

    KConfigurableConditionalEdgeV1(**flow)
    KConfigurableConditionalEdge(**flow)