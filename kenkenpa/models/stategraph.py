"""
This module defines data models for state graphs using Pydantic for validation.
It includes models for state definitions, state graph parameters,
and state graphs themselves, ensuring that certain constraints are met.
"""
from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict

from kenkenpa.models.edge import KEdge
from kenkenpa.models.node import KNode
from kenkenpa.models.configurable_conditional_edge import KConfigurableConditionalEdge
from kenkenpa.models.configurable_conditional_entry_point import KConfigurableConditionalEntryPoint


class KStateV1(BaseModel):
    """
    KStateV1 represents the state with a field name, type, and an optional reducer.

    Attributes:
        field_name (str): The name of the field.
        type (str): The type of the state.
        reducer (Optional[str]): An optional reducer for the state.
    """
    field_name:str
    type:str
    reducer:Optional[Union[str,None]] = None

    model_config = ConfigDict(extra='forbid')

KState = Union[KStateV1]

class KStateGraphParamV1(BaseModel):
    """
    KStateGraphParamV1 represents the parameters for a state graph.

    Attributes:
        name (str): The name of the state graph.
        state (Optional[List[KState]]): An optional list of states in the graph.
    """
    name: str
    state: Optional[Union[List[KState]]] = None

KStateGraphParam = Union[KStateGraphParamV1]

class KStateGraphV1(BaseModel):
    """
    KStateGraphV1 represents a state graph with a type, flow parameters, and flows.

    Attributes:
        graph_type (str): The type of the graph.
        flow_parameter (KStateGraphParam): The parameters for the state graph.
        flows (List[Union[KEdge, KNode, KConfigurableConditionalEdge,
            KConfigurableConditionalEntryPoint, 'KStateGraph']]):
            A list of flows in the graph.
    """
    graph_type:str
    flow_parameter:KStateGraphParam
    flows:List[Union[
        KEdge,
        KNode,
        KConfigurableConditionalEdge,
        KConfigurableConditionalEntryPoint,
        'KStateGraph'
    ]]

KStateGraph = Union[KStateGraphV1]
