"""
This module defines data models for various types of operands,
expressions, and conditions using Pydantic for validation.
It includes models for operand functions, state values,
config values, scalar values, logical expressions, and conditions.
"""
from typing import List, Union, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class KOperandFunctionV1(BaseModel):
    """
    KOperandFunctionV1 represents a function operand with its type, name, and optional arguments.

    Attributes:
        type (str): The type of the function.
        name (str): The name of the function.
        args (Optional[Dict[str, Any]]): Optional arguments for the function.
    """
    type: str
    name: str
    args: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra='forbid')

KOperandFunction = Union[KOperandFunctionV1]

class KOperandStateValueV1(BaseModel):
    """
    KOperandStateValueV1 represents a state value operand with its type and name.

    Attributes:
        type (str): The type of the state value.
        name (str): The name of the state value.
    """
    type: str
    name: str

    model_config = ConfigDict(extra='forbid')

KOperandStateValue = Union[KOperandStateValueV1]

class KOperandConfigValueV1(BaseModel):
    """
    KOperandConfigValueV1 represents a configuration value operand with its type and name.

    Attributes:
        type (str): The type of the configuration value.
        name (str): The name of the configuration value.
    """
    type: str
    name: str

    model_config = ConfigDict(extra='forbid')

KOperandConfigValue = Union[KOperandConfigValueV1]

KOperandScalarV1 = Union[int,float,complex,bool,str,bytes,None]
KOperandScalar = Union[KOperandScalarV1]

KOperandV1 = Union[KOperandScalar,KOperandFunction,KOperandStateValue,KOperandConfigValue]
KOperand = Union[KOperandV1]

class KExpressionV1(BaseModel):
    """
    KExpressionV1 represents a logical expression with various comparison operators.

    Attributes:
        and_ (Optional[List['KExpressionV1']]):
            Logical AND expressions.
        or_ (Optional[List['KExpressionV1']]):
            Logical OR expressions.
        not_ (Optional['KExpressionV1']):
            Logical NOT expression.
        eq_ (Optional[List[KOperand]]):
            Equality comparison operands.
        equals (Optional[List[KOperand]]):
            Alternative equality comparison operands.
        eq (Optional[List[KOperand]]):
            Another alternative equality comparison operands.
        neq_ (Optional[List[KOperand]]):
            Inequality comparison operands.
        not_equals (Optional[List[KOperand]]):
            Alternative inequality comparison operands.
        neq (Optional[List[KOperand]]):
            Another alternative inequality comparison operands.
        gt_ (Optional[List[KOperand]]):
            Greater than comparison operands.
        greater_than (Optional[List[KOperand]]):
            Alternative greater than comparison operands.
        gt (Optional[List[KOperand]]): Another alternative greater than comparison operands.
        gte_ (Optional[List[KOperand]]):
            Greater than or equal to comparison operands.
        greater_than_or_equals (Optional[List[KOperand]]):
            Alternative greater than or equal to comparison operands.
        gte (Optional[List[KOperand]]):
            Another alternative greater than or equal to comparison operands.
        lt_ (Optional[List[KOperand]]):
            Less than comparison operands.
        less_than (Optional[List[KOperand]]):
            Alternative less than comparison operands.
        lt (Optional[List[KOperand]]):
            Another alternative less than comparison operands.
        lte_ (Optional[List[KOperand]]):
            Less than or equal to comparison operands.
        less_than_or_equals (Optional[List[KOperand]]):
            Alternative less than or equal to comparison operands.
        lte (Optional[List[KOperand]]):
            Another alternative less than or equal to comparison operands.
    """
    and_ : Optional[List['KExpressionV1']] = Field(None,alias='and')
    or_ : Optional[List['KExpressionV1']] = Field(None,alias='or')
    not_ : Optional['KExpressionV1'] = Field(None,alias='not')

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

KExpression = Union[KExpressionV1]

KConcitionResult = Union[str,KOperandFunction,KOperandStateValue,KOperandConfigValue]
KConcitionResultList = List[KConcitionResult]

class KConditionExpressionV1(BaseModel):
    """
    KConditionExpressionV1 represents a condition expression with an expression and a result.

    Attributes:
        expression (Union[KExpression]): The logical expression.
        result (Union[KConcitionResult,KConcitionResultList]): The result of the condition.
    """
    expression: Union[KExpression] = None
    result: Union[KConcitionResult,KConcitionResultList] = None

    model_config = ConfigDict(extra='forbid')

KConditionExpression = Union[KConditionExpressionV1]

class KConditionDefaultV1(BaseModel):
    """
    KConditionDefaultV1 represents a default condition with a default value.

    Attributes:
        default (Union[KConcitionResult,KConcitionResultList]): The default value.
    """
    default: Union[KConcitionResult,KConcitionResultList] = None

    model_config = ConfigDict(extra='forbid')

KConditionDefault = Union[KConditionDefaultV1]


class KConditionsV1(BaseModel):
    """
    KConditionsV1 represents a collection of conditions.

    Attributes:
        conditions (List[Union[KConditionExpression, KConditionDefault]]):
            A list of condition expressions and default conditions.
    """
    conditions:List[Union[KConditionExpression,KConditionDefault]]

    model_config = ConfigDict(extra='forbid')

KConditions = Union[KConditionsV1]
