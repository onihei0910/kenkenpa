from pydantic import BaseModel, ValidationError,ConfigDict
from typing import List, Optional, Union, Dict, Any

class KEdgeParam_v1(BaseModel):
    start_key: Union[List[str],str]
    end_key: Union[List[str],str]

    model_config = ConfigDict(extra='forbid')

KEdgeParam = Union[KEdgeParam_v1]


class KEdge_v1(BaseModel):
    graph_type: str
    flow_parameter: KEdgeParam

    model_config = ConfigDict(extra='forbid')

KEdge = Union[KEdge_v1]
