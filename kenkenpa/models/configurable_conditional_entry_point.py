"""
This module defines data models for conditional entry point flow parameters and
configurable conditional entry points using Pydantic for validation.
It includes models for conditional entry point flow parameters and
configurable conditional entry points, ensuring that certain constraints are met.

Classes:
    KConditionalEntryPointFlowParamV1:
        Represents the flow parameters for a conditional entry point.
    KConfigurableConditionalEntryPointV1:
        Represents a configurable conditional entry point in a graph.

Type Aliases:
    KConditionalEntryPointFlowParam: Alias for KConditionalEntryPointFlowParamV1.
    KConfigurableConditionalEntryPoint: Alias for KConfigurableConditionalEntryPointV1.
"""
from typing import List, Union, Optional
from pydantic import BaseModel, ConfigDict

from kenkenpa.models.conditions import KConditionExpression
from kenkenpa.models.conditions import KConditionDefault


class KConditionalEntryPointFlowParamV1(BaseModel):
    """
    KConditionalEntryPointFlowParamV1 represents
    the flow parameters for a conditional entry point.

    Attributes:
        path_map (Optional[List[str]]): An optional list of path mappings.
        conditions (List[Union[KConditionExpression, KConditionDefault]]):
            A list of conditions for the entry point.
    """
    path_map:Optional[List[str]] = None
    conditions:List[Union[KConditionExpression,KConditionDefault]]

    model_config = ConfigDict(extra='forbid')

KConditionalEntryPointFlowParam = Union[KConditionalEntryPointFlowParamV1]

class KConfigurableConditionalEntryPointV1(BaseModel):
    """
    KConfigurableConditionalEntryPointV1 represents
    a configurable conditional entry point in a graph.

    Attributes:
        graph_type (str): The type of the graph.
        flow_parameter (KConditionalEntryPointFlowParam):
            The flow parameters for the conditional entry point.
    """
    graph_type:str
    flow_parameter:KConditionalEntryPointFlowParam

    model_config = ConfigDict(extra='forbid')

KConfigurableConditionalEntryPoint = Union[KConfigurableConditionalEntryPointV1]
