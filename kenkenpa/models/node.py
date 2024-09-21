from pydantic import BaseModel, ConfigDict
from typing import Optional, Union, Dict

## ノードフローパラメータ定義
class KNodeParam_v1(BaseModel):
    name:str
    factory:str

    model_config = ConfigDict(extra='forbid')

KNodeParam = Union[KNodeParam_v1]

# ノードフロー定義
class KNode_v1(BaseModel):
    graph_type: str
    flow_parameter: KNodeParam
    factory_parameter: Optional[Union[Dict]] = None

    model_config = ConfigDict(extra='forbid')

KNode = Union[KNode_v1]