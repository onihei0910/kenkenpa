from pydantic import BaseModel, ConfigDict,field_validator
from typing import List, Union

class KEdgeParam_v1(BaseModel):
    start_key: Union[List[str],str]
    end_key: Union[List[str],str]

    model_config = ConfigDict(extra='forbid')

    @field_validator('end_key', mode='before')
    def check_keys(cls, v, values):
        start_key = values.data.get('start_key')
        if isinstance(start_key,list) and isinstance(v,list):
            raise ValueError('start_key または end_keyのいずれか一方のみがリストでなければなりません。')
        return v

KEdgeParam = Union[KEdgeParam_v1]

class KEdge_v1(BaseModel):
    graph_type: str
    flow_parameter: KEdgeParam

    model_config = ConfigDict(extra='forbid')

KEdge = Union[KEdge_v1]
