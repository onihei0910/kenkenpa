from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict

from kenkenpa.models.edge import KEdge
from kenkenpa.models.node import KNode
from kenkenpa.models.static_conditional_edge import StaticConditionalEdge
from kenkenpa.models.static_conditional_entry_point import StaticConditionalEntoryPoint


class KState_v1(BaseModel):
    field_name:str
    type:str
    reducer:Optional[Union[str,None]] = None

    model_config = ConfigDict(extra='forbid')

KState = Union[KState_v1]

class KStateGraphParam_v1(BaseModel):
    name: str
    state: Optional[Union[List[KState]]] = None

KStateGraphParam = Union[KStateGraphParam_v1]

class KStateGraph_v1(BaseModel):
    graph_type:str
    flow_parameter:KStateGraphParam
    flows:List[Union[
        KEdge,
        KNode,
        StaticConditionalEdge,
        StaticConditionalEntoryPoint,
        'KStateGraph'
    ]]

KStateGraph = Union[KStateGraph_v1]