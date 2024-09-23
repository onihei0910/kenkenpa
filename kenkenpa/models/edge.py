"""
This module defines data models for graph edges using Pydantic for validation.
It includes models for edge parameters and edges themselves, ensuring that
certain constraints are met.
"""
from pydantic import BaseModel, ConfigDict,field_validator
from typing import List, Union

class KEdgeParam_v1(BaseModel):
    """
    KEdgeParam_v1 represents the parameters for a graph edge, including start and end keys.

    Attributes:
        start_key (Union[List[str], str]): The starting key(s) for the edge.
        end_key (Union[List[str], str]): The ending key(s) for the edge.
    """
    start_key: Union[List[str],str]
    end_key: Union[List[str],str]

    model_config = ConfigDict(extra='forbid')

    @field_validator('end_key', mode='before')
    def check_keys(cls, v, values):
        """
        Validates that only one of start_key or end_key is a list.

        Args:
            v: The value of the end_key field.
            values: A dictionary containing the values of other fields.

        Raises:
            ValueError: If both start_key and end_key are lists.

        Returns:
            The validated value of end_key.
        """
        start_key = values.data.get('start_key')
        if isinstance(start_key,list) and isinstance(v,list):
            raise ValueError('start_key または end_keyのいずれか一方のみがリストでなければなりません。')
        return v

KEdgeParam = Union[KEdgeParam_v1]

class KEdge_v1(BaseModel):
    """
    KEdge_v1 represents an edge in a graph, including the type of graph and flow parameters.

    Attributes:
        graph_type (str): The type of the graph.
        flow_parameter (KEdgeParam): The parameters for the edge.
    """
    graph_type: str
    flow_parameter: KEdgeParam

    model_config = ConfigDict(extra='forbid')

KEdge = Union[KEdge_v1]
