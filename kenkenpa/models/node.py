"""
This module defines data models for graph nodes using Pydantic for validation.
It includes models for node parameters and nodes themselves, ensuring that
certain constraints are met.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Union, Dict

class KNodeParam_v1(BaseModel):
    """
    KNodeParam_v1 represents the parameters for a graph node.

    Attributes:
        name (str): The name of the node.
        factory (str): The factory associated with the node.
    """
    name:str
    factory:str

    model_config = ConfigDict(extra='forbid')

KNodeParam = Union[KNodeParam_v1]

class KNode_v1(BaseModel):
    """
    KNode_v1 represents a node in a graph, including the type of graph and flow parameters.

    Attributes:
        graph_type (str): The type of the graph.
        flow_parameter (KNodeParam): The parameters for the node.
        factory_parameter (Optional[Dict]): Optional factory parameters for the node.
    """
    graph_type: str
    flow_parameter: KNodeParam
    factory_parameter: Optional[Dict] = None

    model_config = ConfigDict(extra='forbid')

KNode = Union[KNode_v1]
