import pytest
from kenkenpa.models.conditions import KOperandFunction_v1
from kenkenpa.models.conditions import KOperandFunction

from kenkenpa.models.conditions import KOperandStateValue_v1
from kenkenpa.models.conditions import KOperandStateValue

from kenkenpa.models.conditions import KOperandConfigValue_v1
from kenkenpa.models.conditions import KOperandConfigValue

from kenkenpa.models.conditions import KExpression_v1
from kenkenpa.models.conditions import KExpression

from kenkenpa.models.conditions import KConditionExpression_v1
from kenkenpa.models.conditions import KConditionExpression

from kenkenpa.models.conditions import KConditionDefault_v1
from kenkenpa.models.conditions import KConditionDefault

from kenkenpa.models.conditions import KConditions_v1
from kenkenpa.models.conditions import KConditions


def test_KOperandFunction_v1():
    operand = {"type":"function","name":"test_function","args":{"args_key":"args_value"}}
    KOperandFunction_v1(**operand)
    KOperandFunction(**operand)

def test_KOperandStateValue_v1():
    operand = {"type":"state_value", "name":"test_state_key"}

    KOperandStateValue_v1(**operand)
    KOperandStateValue(**operand)

def test_KOperandConfigValue_v1():
    operand = {"type":"config_value", "name":"test_config_key"}


    KOperandConfigValue_v1(**operand)
    KOperandConfigValue(**operand)

def test_KOperandScalar_v1():
    operater = {"and": [{"eq": ["", ""]}]}
    KExpression_v1(**operater)
    KExpression(**operater)

    operater = {"and":[{"eq": ["", ""]},{"or":[{"eq": ["", ""]}]}]}
    KExpression_v1(**operater)
    KExpression(**operater)

    operater = {"or":[{"eq": ["", ""]}]}
    KExpression_v1(**operater)
    KExpression(**operater)

    operater = {"or":[{"eq": ["", ""]},{"and":[{"eq": ["", ""]}]}]}
    KExpression_v1(**operater)
    KExpression(**operater)

    operater = {"not":{"eq": ["", ""]}}
    KExpression_v1(**operater)
    KExpression(**operater)

    operater = {"not":{"and":[{"eq": ["", ""]},{"or":[{"eq": ["", ""]},{"and":[{"eq": ["", ""]}]}]}]}}
    KExpression_v1(**operater)
    KExpression(**operater)

    operater = {"==": ["", ""]}
    KExpression_v1(**operater)
    KExpression(**operater)
    operater = {"equals": ["", ""]}
    KExpression_v1(**operater)
    KExpression(**operater)
    operater = {"eq": ["", ""]}
    KExpression_v1(**operater)
    KExpression(**operater)

    operater = {"!=": ["", ""]}
    KExpression_v1(**operater)
    KExpression(**operater)
    operater = {"not_equals": ["", ""]}
    KExpression_v1(**operater)
    KExpression(**operater)
    operater = {"neq": ["", ""]}
    KExpression_v1(**operater)
    KExpression(**operater)

    operater = {">": ["", ""]}
    KExpression_v1(**operater)
    KExpression(**operater)
    operater = {"greater_than": ["", ""]}
    KExpression_v1(**operater)
    KExpression(**operater)
    operater = {"gt": ["", ""]}
    KExpression_v1(**operater)
    KExpression(**operater)

    operater = {">=": ["", ""]}
    KExpression_v1(**operater)
    KExpression(**operater)
    operater = {"greater_than_or_equals": ["", ""]}
    KExpression_v1(**operater)
    KExpression(**operater)
    operater = {"gte": ["", ""]}
    KExpression_v1(**operater)
    KExpression(**operater)

    operater = {"<": ["", ""]}
    KExpression_v1(**operater)
    KExpression(**operater)
    operater = {"less_than": ["", ""]}
    KExpression_v1(**operater)
    KExpression(**operater)
    operater = {"lt": ["", ""]}
    KExpression_v1(**operater)
    KExpression(**operater)

    operater = {"<=": ["", ""]}
    KExpression_v1(**operater)
    KExpression(**operater)
    operater = {"less_than_or_equals": ["", ""]}
    KExpression_v1(**operater)
    KExpression(**operater)
    operater = {"lte": ["", ""]}
    KExpression_v1(**operater)
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
    KConditionExpression_v1(**condition)
    KConditionExpression(**condition)

    condition = {"default": "Default_Value"} 
    KConditionDefault_v1(**condition)
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
    KConditions_v1(**conditions)
    KConditions(**conditions)