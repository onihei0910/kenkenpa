"""
This module defines data models for conditional edge flow parameters and static conditional edges using Pydantic for validation.
It includes models for conditional edge flow parameters and static conditional edges, ensuring that certain constraints are met.
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
        conditions (List[Union[KConditionExpression, KConditionDefault]]): A list of conditions for the edge.
    """
    start_key:str
    conditions:List[Union[KConditionExpression,KConditionDefault]]
    path_map:Optional[List[str]] = None

    model_config = ConfigDict(extra='forbid')

KConditionalEdgeFlowParam = Union[KConditionalEdgeFlowParam_v1]

class KStaticConditionalEdge_v1(BaseModel):
    """
    KStaticConditionalEdge_v1 represents a static conditional edge in a graph.

    Attributes:
        graph_type (str): The type of the graph.
        flow_parameter (KConditionalEdgeFlowParam): The flow parameters for the conditional edge.
    """
    graph_type:str
    flow_parameter:KConditionalEdgeFlowParam

    model_config = ConfigDict(extra='forbid')

KStaticConditionalEdge = Union[KStaticConditionalEdge_v1]


