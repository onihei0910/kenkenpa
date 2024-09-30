import pytest
from kenkenpa.models.configurable_conditional_entry_point import KConditionalEntryPointFlowParamV1
from kenkenpa.models.configurable_conditional_entry_point import KConditionalEntryPointFlowParam

from kenkenpa.models.configurable_conditional_entry_point import KConfigurableConditionalEntryPointV1
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

    KConditionalEntryPointFlowParamV1(**flow_parameter)
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

    KConditionalEntryPointFlowParamV1(**flow_parameter)
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

    KConfigurableConditionalEntryPointV1(**flow)
    KConfigurableConditionalEntryPoint(**flow)