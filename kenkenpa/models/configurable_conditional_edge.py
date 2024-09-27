"""
This module defines data models for conditional edge flow parameters and
configurable conditional edges using Pydantic for validation.
It includes models for conditional edge flow parameters and
configurable conditional edges, ensuring that certain constraints are met.

Classes:
    KConditionalEdgeFlowParam_v1: Represents the flow parameters for a conditional edge.
    KConfigurableConditionalEdge_v1: Represents a configurable conditional edge in a graph.

Type Aliases:
    KConditionalEdgeFlowParam: Alias for KConditionalEdgeFlowParam_v1.
    KConfigurableConditionalEdge: Alias for KConfigurableConditionalEdge_v1.
"""
from typing import List, Union, Optional
from pydantic import BaseModel, ConfigDict

from kenkenpa.models.conditions import KConditionExpression
from kenkenpa.models.conditions import KConditionDefault

class KConditionalEdgeFlowParam_v1(BaseModel):
    """
    KConditionalEdgeFlowParam_v1 represents the flow parameters for a conditional edge.

    Attributes:
        start_key (str): The starting key for the edge.
        path_map (Optional[List[str]]): An optional list of path mappings.
        conditions (List[Union[KConditionExpression, KConditionDefault]]):
            A list of conditions for the edge.
    """
    start_key:str
    path_map:Optional[List[str]] = None
    conditions:List[Union[KConditionExpression,KConditionDefault]]

    model_config = ConfigDict(extra='forbid')

KConditionalEdgeFlowParam = Union[KConditionalEdgeFlowParam_v1]

class KConfigurableConditionalEdge_v1(BaseModel):
    """
    KConfigurableConditionalEdge_v1 represents a configurable conditional edge in a graph.

    Attributes:
        graph_type (str): The type of the graph.
        flow_parameter (KConditionalEdgeFlowParam): The flow parameters for the conditional edge.
    """
    graph_type:str
    flow_parameter:KConditionalEdgeFlowParam

    model_config = ConfigDict(extra='forbid')

KConfigurableConditionalEdge = Union[KConfigurableConditionalEdge_v1]
