import pytest
from kenkenpa.models.conditions import KOperandFunctionV1
from kenkenpa.models.conditions import KOperandFunction

from kenkenpa.models.conditions import KOperandStateValueV1
from kenkenpa.models.conditions import KOperandStateValue

from kenkenpa.models.conditions import KOperandConfigValueV1
from kenkenpa.models.conditions import KOperandConfigValue

from kenkenpa.models.conditions import KExpressionV1
from kenkenpa.models.conditions import KExpression

from kenkenpa.models.conditions import KConditionExpressionV1
from kenkenpa.models.conditions import KConditionExpression

from kenkenpa.models.conditions import KConditionDefaultV1
from kenkenpa.models.conditions import KConditionDefault

from kenkenpa.models.conditions import KConditionsV1
from kenkenpa.models.conditions import KConditions


def test_KOperandFunctionV1():
    operand = {"type":"function","name":"test_function","args":{"args_key":"args_value"}}
    KOperandFunctionV1(**operand)
    KOperandFunction(**operand)

def test_KOperandStateValueV1():
    operand = {"type":"state_value", "name":"test_state_key"}

    KOperandStateValueV1(**operand)
    KOperandStateValue(**operand)

def test_KOperandConfigValueV1():
    operand = {"type":"config_value", "name":"test_config_key"}


    KOperandConfigValueV1(**operand)
    KOperandConfigValue(**operand)

def test_KOperandScalarV1():
    operater = {"and": [{"eq": ["", ""]}]}
    KExpressionV1(**operater)
    KExpression(**operater)

    operater = {"and":[{"eq": ["", ""]},{"or":[{"eq": ["", ""]}]}]}
    KExpressionV1(**operater)
    KExpression(**operater)

    operater = {"or":[{"eq": ["", ""]}]}
    KExpressionV1(**operater)
    KExpression(**operater)

    operater = {"or":[{"eq": ["", ""]},{"and":[{"eq": ["", ""]}]}]}
    KExpressionV1(**operater)
    KExpression(**operater)

    operater = {"not":{"eq": ["", ""]}}
    KExpressionV1(**operater)
    KExpression(**operater)

    operater = {"not":{"and":[{"eq": ["", ""]},{"or":[{"eq": ["", ""]},{"and":[{"eq": ["", ""]}]}]}]}}
    KExpressionV1(**operater)
    KExpression(**operater)

    operater = {"==": ["", ""]}
    KExpressionV1(**operater)
    KExpression(**operater)
    operater = {"equals": ["", ""]}
    KExpressionV1(**operater)
    KExpression(**operater)
    operater = {"eq": ["", ""]}
    KExpressionV1(**operater)
    KExpression(**operater)

    operater = {"!=": ["", ""]}
    KExpressionV1(**operater)
    KExpression(**operater)
    operater = {"not_equals": ["", ""]}
    KExpressionV1(**operater)
    KExpression(**operater)
    operater = {"neq": ["", ""]}
    KExpressionV1(**operater)
    KExpression(**operater)

    operater = {">": ["", ""]}
    KExpressionV1(**operater)
    KExpression(**operater)
    operater = {"greater_than": ["", ""]}
    KExpressionV1(**operater)
    KExpression(**operater)
    operater = {"gt": ["", ""]}
    KExpressionV1(**operater)
    KExpression(**operater)

    operater = {">=": ["", ""]}
    KExpressionV1(**operater)
    KExpression(**operater)
    operater = {"greater_than_or_equals": ["", ""]}
    KExpressionV1(**operater)
    KExpression(**operater)
    operater = {"gte": ["", ""]}
    KExpressionV1(**operater)
    KExpression(**operater)

    operater = {"<": ["", ""]}
    KExpressionV1(**operater)
    KExpression(**operater)
    operater = {"less_than": ["", ""]}
    KExpressionV1(**operater)
    KExpression(**operater)
    operater = {"lt": ["", ""]}
    KExpressionV1(**operater)
    KExpression(**operater)

    operater = {"<=": ["", ""]}
    KExpressionV1(**operater)
    KExpression(**operater)
    operater = {"less_than_or_equals": ["", ""]}
    KExpressionV1(**operater)
    KExpression(**operater)
    operater = {"lte": ["", ""]}
    KExpressionV1(**operater)
    KExpression(**operater)

def test_KCondition():
    condition = {
        "expression": {
            "and":[
                {"eq": ["10", "10"]},
                {"eq": ["10", "10"]},
                {"eq": ["10", "10"]},
            ],
        },
        "result": "Result_Value"
    }
    KConditionExpressionV1(**condition)
    KConditionExpression(**condition)

    condition = {
        "expression": {
            "eq": ["10", "10"],
        },
        "result": {"type":"function","name":"test_function","args":{"args_key":"args_value"}} 
    }
    KConditionExpressionV1(**condition)
    KConditionExpression(**condition)

    condition = {
        "expression": {
            "eq": ["10", "10"],
        },
        "result": {"type":"state_value", "name":"test_state_key"}
    }

    condition = {
        "expression": {
            "eq": ["10", "10"],
        },
        "result": {"type":"config_value", "name":"test_config_key"}
    }
    KConditionExpressionV1(**condition)
    KConditionExpression(**condition)

    condition = {"default": "Default_Value"} 
    KConditionDefaultV1(**condition)
    KConditionDefault(**condition)

    condition = {"default":
        {"type":"function","name":"test_function","args":{"args_key":"args_value"}}
    }
    KConditionDefaultV1(**condition)
    KConditionDefault(**condition)

    condition = {"default":
        {"type":"state_value", "name":"test_state_key"}
    }
    KConditionDefaultV1(**condition)
    KConditionDefault(**condition)

    condition = {"default":
        {"type":"config_value", "name":"test_config_key"}

    }
    KConditionDefaultV1(**condition)
    KConditionDefault(**condition)

    conditions = {
        "conditions":[
            {
                "expression": {
                    "eq": [
                        {"type": "function", "name": "is_tool_message_function"},
                        True
                        ],
                },
                "result": "tools"
            },
            {"default": "END"} 
        ]
    }
    KConditionsV1(**conditions)
    KConditions(**conditions)

