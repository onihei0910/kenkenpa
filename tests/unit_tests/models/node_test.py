import pytest

from kenkenpa.models.node import KNodeParam_v1
from kenkenpa.models.node import KNodeParam

from kenkenpa.models.node import KNode_v1
from kenkenpa.models.node import KNode

def test_KNodeFlowParam():
    frow_parameter = {
        "name":"tools",
        "factory":"tool_node_factory",
    }
    KNodeParam_v1(**frow_parameter)
    KNodeParam(**frow_parameter)

def test_KNode():
    flow = {
        "graph_type":"node",
        "flow_parameter":{
            "name":"agent",
            "factory":"agent_node_factory",
        },
        "factory_parameter" : {
            "functions":[
                "search_function",
            ],
        },
    }

    KNode_v1(**flow)
    KNode(**flow)

    flow = {
        "graph_type":"node",
        "flow_parameter":{
            "name":"agent",
            "factory":"agent_node_factory",
        },
    }

    KNode_v1(**flow)
    KNode(**flow)

