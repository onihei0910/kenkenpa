import pytest

from kenkenpa.models.edge import KEdgeParamV1
from kenkenpa.models.edge import KEdgeParam

from kenkenpa.models.edge import KEdgeV1
from kenkenpa.models.edge import KEdge

def test_KEdgeParam():
    flow_parameter = {
        "start_key":"START",
        "end_key":"agent"
    }

    KEdgeParamV1(**flow_parameter)
    KEdgeParam(**flow_parameter)

    flow_parameter = {
        "start_key":["A","B"],
        "end_key":["C","D"]
    }

    exc_info = pytest.raises(ValueError, KEdgeParamV1, **flow_parameter)
    assert "You can only list either the start_key or the end_key." in str(exc_info.value)

    exc_info = pytest.raises(ValueError, KEdgeParam, **flow_parameter)
    assert "You can only list either the start_key or the end_key." in str(exc_info.value)

def test_KEdge():
    flow = {
        "graph_type":"edge",
        "flow_parameter":{
            "start_key":"START",
            "end_key":"agent"
        },
    }

    KEdgeV1(**flow)
    KEdge(**flow)