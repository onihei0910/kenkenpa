"""
This module defines data models for conditional entry point flow parameters and
configurable conditional entry points using Pydantic for validation.
It includes models for conditional entry point flow parameters and
configurable conditional entry points, ensuring that certain constraints are met.

Classes:
    KConditionalEntryPointFlowParam_v1:
        Represents the flow parameters for a conditional entry point.
    KConfigurableConditionalEntryPoint_v1:
        Represents a configurable conditional entry point in a graph.

Type Aliases:
    KConditionalEntryPointFlowParam: Alias for KConditionalEntryPointFlowParam_v1.
    KConfigurableConditionalEntryPoint: Alias for KConfigurableConditionalEntryPoint_v1.
"""
from typing import List, Union, Optional
from pydantic import BaseModel, ConfigDict

from kenkenpa.models.conditions import KConditionExpression
from kenkenpa.models.conditions import KConditionDefault


class KConditionalEntryPointFlowParam_v1(BaseModel):
    """
    KConditionalEntryPointFlowParam_v1 represents
    the flow parameters for a conditional entry point.

    Attributes:
        path_map (Optional[List[str]]): An optional list of path mappings.
        conditions (List[Union[KConditionExpression, KConditionDefault]]):
            A list of conditions for the entry point.
    """
    path_map:Optional[List[str]] = None
    conditions:List[Union[KConditionExpression,KConditionDefault]]

    model_config = ConfigDict(extra='forbid')

KConditionalEntryPointFlowParam = Union[KConditionalEntryPointFlowParam_v1]

class KConfigurableConditionalEntryPoint_v1(BaseModel):
    """
    KConfigurableConditionalEntryPoint_v1 represents
    a configurable conditional entry point in a graph.

    Attributes:
        graph_type (str): The type of the graph.
        flow_parameter (KConditionalEntryPointFlowParam):
            The flow parameters for the conditional entry point.
    """
    graph_type:str
    flow_parameter:KConditionalEntryPointFlowParam

    model_config = ConfigDict(extra='forbid')

KConfigurableConditionalEntryPoint = Union[KConfigurableConditionalEntryPoint_v1]
