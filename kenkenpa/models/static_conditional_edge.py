from typing import List, Union
from pydantic import BaseModel, ConfigDict

from kenkenpa.models.conditions import KConditionExpression
from kenkenpa.models.conditions import KConditionDefault

class KConditionalEdgeFlowParam_v1(BaseModel):
    start_key:str
    conditions:List[Union[KConditionExpression,KConditionDefault]]

    model_config = ConfigDict(extra='forbid')

KConditionalEdgeFlowParam = Union[KConditionalEdgeFlowParam_v1]

class StaticConditionalEdge_v1(BaseModel):
    graph_type:str
    flow_parameter:KConditionalEdgeFlowParam
    model_config = ConfigDict(extra='forbid')

StaticConditionalEdge = Union[StaticConditionalEdge_v1]


