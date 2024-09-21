from typing import List, Union, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class KOperandFunction_v1(BaseModel):
    type: str
    name: str
    args: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra='forbid')

KOperandFunction = Union[KOperandFunction_v1]

class KOperandStateValue_v1(BaseModel):
    type: str
    name: str

    model_config = ConfigDict(extra='forbid')

KOperandStateValue = Union[KOperandFunction_v1]

class KOperandConfigValue_v1(BaseModel):
    type: str
    name: str

    model_config = ConfigDict(extra='forbid')

KOperandConfigValue = Union[KOperandConfigValue_v1]

KOperandScalar_v1 = Union[int,float,complex,bool,str,bytes,None]
KOperandScalar = Union[KOperandScalar_v1]

KOperand_v1 = Union[KOperandScalar,KOperandFunction,KOperandStateValue,KOperandConfigValue]
KOperand = Union[KOperand_v1]

class KExpression_v1(BaseModel):
    and_ : Optional[List['KExpression_v1']] = Field(None,alias='and')
    or_ : Optional[List['KExpression_v1']] = Field(None,alias='or')
    not_ : Optional['KExpression_v1'] = Field(None,alias='not')

    eq_: Optional[List[KOperand]] = Field(None,alias='==')
    equals: Optional[List[KOperand]] = None
    eq: Optional[List[KOperand]] = None

    neq_: Optional[List[KOperand]] = Field(None,alias='!=')    
    not_equals: Optional[List[KOperand]] = None
    neq: Optional[List[KOperand]] = None

    gt_: Optional[List[KOperand]] = Field(None,alias='>')
    greater_than: Optional[List[KOperand]] = None
    gt: Optional[List[KOperand]] = None

    gte_: Optional[List[KOperand]] = Field(None,alias='>=')
    greater_than_or_equals: Optional[List[KOperand]] = None
    gte: Optional[List[KOperand]] = None

    lt_: Optional[List[KOperand]] = Field(None,alias='<')
    less_than: Optional[List[KOperand]] = None
    lt: Optional[List[KOperand]] = None

    lte_: Optional[List[KOperand]] = Field(None,alias='<=')
    less_than_or_equals: Optional[List[KOperand]] = None
    lte: Optional[List[KOperand]] = None

    model_config = ConfigDict(extra='forbid')

KExpression = Union[KExpression_v1]

class KConditionExpression_v1(BaseModel):
    expression: Union[KExpression] = None
    result: Union[str, List[str]] = None

    model_config = ConfigDict(extra='forbid')

KConditionExpression = Union[KConditionExpression_v1]

class KConditionDefault_v1(BaseModel):
    default: Union[str, List[str]] = None

    model_config = ConfigDict(extra='forbid')

KConditionDefault = Union[KConditionDefault_v1]


class KConditions_v1(BaseModel):
    conditions:List[Union[KConditionExpression,KConditionDefault]]

    model_config = ConfigDict(extra='forbid')

KConditions = Union[KConditions_v1]