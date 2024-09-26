import pytest
from kenkenpa.models.configurable_conditional_entry_point import KConditionalEntryPointFlowParam_v1
from kenkenpa.models.configurable_conditional_entry_point import KConditionalEntryPointFlowParam

from kenkenpa.models.configurable_conditional_entry_point import KConfigurableConditionalEntryPoint_v1
from kenkenpa.models.configurable_conditional_entry_point import KConfigurableConditionalEntryPoint

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

    KConditionalEntryPointFlowParam_v1(**flow_parameter)
    KConditionalEntryPointFlowParam(**flow_parameter)

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

    KConditionalEntryPointFlowParam_v1(**flow_parameter)
    KConditionalEntryPointFlowParam(**flow_parameter)

def test_KConfigurableConditionalEdge():
    flow = {
            "graph_type":"configurable_conditional_entry_point",
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
    
    KConfigurableConditionalEntryPoint_v1(**flow)
    KConfigurableConditionalEntryPoint(**flow)