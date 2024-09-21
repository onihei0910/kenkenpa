import pytest

from kenkenpa.models.edge import KEdgeParam_v1
from kenkenpa.models.edge import KEdgeParam

from kenkenpa.models.edge import KEdge_v1
from kenkenpa.models.edge import KEdge

def test_KEdgeParam():
    flow_parameter = {
        "start_key":"START",
        "end_key":"agent"
    }

    KEdgeParam_v1(**flow_parameter)
    KEdgeParam(**flow_parameter)

def test_KEdge():
    flow = {
        "graph_type":"edge",
        "flow_parameter":{
            "start_key":"START",
            "end_key":"agent"
        },
    }

    KEdge_v1(**flow)
    KEdge(**flow)