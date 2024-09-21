from pydantic import BaseModel, ConfigDict
from typing import List, Union

from kenkenpa.models.conditions import KConditionExpression
from kenkenpa.models.conditions import KConditionDefault


class KConditionalEntoryPointFlowParam_v1(BaseModel):
    conditions:List[Union[KConditionExpression,KConditionDefault]]

    model_config = ConfigDict(extra='forbid')

KConditionalEntoryPointFlowParam = Union[KConditionalEntoryPointFlowParam_v1]

class StaticConditionalEntoryPoint_v1(BaseModel):
    graph_type:str
    flow_parameter:KConditionalEntoryPointFlowParam
    
    model_config = ConfigDict(extra='forbid')

StaticConditionalEntoryPoint = Union[StaticConditionalEntoryPoint_v1]


