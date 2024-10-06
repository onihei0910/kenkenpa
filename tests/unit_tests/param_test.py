import pytest

from kenkenpa.models.stategraph import KStateGraphV1,KStateV1
from kenkenpa.models.node import KNodeV1
from kenkenpa.models.edge import KEdgeV1
from kenkenpa.models.configurable_conditional_edge import KConfigurableConditionalEdgeV1
from kenkenpa.models.configurable_conditional_entry_point import KConfigurableConditionalEntryPointV1
from kenkenpa.models.conditions import KConditionExpressionV1,KConditionDefaultV1

from kenkenpa.models.conditions import (
    KExpressionV1,
    KOperandFunctionV1,
    KOperandStateValueV1,
    KOperandConfigValueV1,
    )

from kenkenpa.param import create_parameter

def test_create_parameter_stategraph():
    param = create_parameter('stategraph')

    KStateGraphV1(**param)

def test_create_parameter_state():
    param = create_parameter('state')
    KStateV1(**param)

def test_create_parameter_node():
    param = create_parameter('node')
    KNodeV1(**param)

def test_create_parameter_edge():
    param = create_parameter('edge')
    KEdgeV1(**param)

def test_create_parameter_conditional_edge():
    param = create_parameter('conditional_edge')
    KConfigurableConditionalEdgeV1(**param)

def test_create_parameter_conditional_endry_point():
    param = create_parameter('conditional_entry_point')
    KConfigurableConditionalEntryPointV1(**param)

def test_create_parameter_condition_expression():
    param = create_parameter('condition_expression')
    KConditionExpressionV1(**param)

def test_create_parameter_condition_default():
    param = create_parameter('condition_default')
    KConditionDefaultV1(**param)

def test_create_parameter_condition_operater():
    param = create_parameter('operater_and')
    KExpressionV1(**param)

    param = create_parameter('operater_or')
    KExpressionV1(**param)

    param = create_parameter('operater_not')
    KExpressionV1(**param)

    param = create_parameter('operater_eq')
    KExpressionV1(**param)

    param = create_parameter('operater_neq')
    KExpressionV1(**param)

    param = create_parameter('operater_gt')
    KExpressionV1(**param)

    param = create_parameter('operater_gte')
    KExpressionV1(**param)

    param = create_parameter('operater_lt')
    KExpressionV1(**param)

    param = create_parameter('operater_lte')
    KExpressionV1(**param)

def test_create_parameter_condition_operand():
    param = create_parameter('operand_function')
    KOperandFunctionV1(**param)

    param = create_parameter('operand_state_value')
    KOperandStateValueV1(**param)

    param = create_parameter('operand_config_value')
    KOperandConfigValueV1(**param)

def test_create_parameter_except():
    with pytest.raises(KeyError) as exc_info:
        create_parameter("some_key")
        assert str(exc_info.value) == "Invalid key: 'some_key'"