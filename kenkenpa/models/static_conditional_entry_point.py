"""
This module defines data models for conditional entry point flow parameters and static conditional entry points using Pydantic for validation.
It includes models for conditional entry point flow parameters and static conditional entry points, ensuring that certain constraints are met.
"""
from pydantic import BaseModel, ConfigDict
from typing import List, Union

from kenkenpa.models.conditions import KConditionExpression
from kenkenpa.models.conditions import KConditionDefault


class KConditionalEntoryPointFlowParam_v1(BaseModel):
    """
    KConditionalEntoryPointFlowParam_v1 represents the flow parameters for a conditional entry point.

    Attributes:
        conditions (List[Union[KConditionExpression, KConditionDefault]]): A list of conditions for the entry point.
    """
    conditions:List[Union[KConditionExpression,KConditionDefault]]

    model_config = ConfigDict(extra='forbid')

KConditionalEntoryPointFlowParam = Union[KConditionalEntoryPointFlowParam_v1]

class KStaticConditionalEntoryPoint_v1(BaseModel):
    """
    KStaticConditionalEntoryPoint_v1 represents a static conditional entry point in a graph.

    Attributes:
        graph_type (str): The type of the graph.
        flow_parameter (KConditionalEntoryPointFlowParam): The flow parameters for the conditional entry point.
    """
    graph_type:str
    flow_parameter:KConditionalEntoryPointFlowParam
    
    model_config = ConfigDict(extra='forbid')

KStaticConditionalEntoryPoint = Union[KStaticConditionalEntoryPoint_v1]


