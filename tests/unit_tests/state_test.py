import pytest
import operator

from typing_extensions import TypedDict, Annotated 

from kenkenpa.state import StateBuilder

def test_statebuilder_primitive_types():
    test_primitive_type_list = {
        "int": int,
        "float": float,
        "complex": complex,
        "str": str,
        "list": list,
        "tuple": tuple,
        "dict": dict,
        "set": set,
        "frozenset": frozenset,
        "bool": bool,
    }
    assert StateBuilder.primitive_type_list == test_primitive_type_list

# Test for getting types from StateBuilder
def test_statebuilder_get_type():
    state_builder = StateBuilder()
    assert state_builder._get_type("int") == int
    assert state_builder._get_type("float") == float
    assert state_builder._get_type("complex") == complex
    assert state_builder._get_type("str") == str
    assert state_builder._get_type("list") == list
    assert state_builder._get_type("tuple") == tuple
    assert state_builder._get_type("dict") == dict
    assert state_builder._get_type("set") == set
    assert state_builder._get_type("frozenset") == frozenset
    assert state_builder._get_type("bool") == bool

# Test for adding reserved types in StateBuilder
def test_statebuilder_add_reserved_types():
    state_builder = StateBuilder()
    reserved_types = ["int", "float", "complex", "str", "list", "tuple", "dict", "set", "frozenset", "bool"]
    for reserved_type in reserved_types:
        with pytest.raises(ValueError, match=f"Reserved type: {reserved_type}"):
            state_builder.add_type(reserved_type, eval(reserved_type))

# Test for adding and getting custom types in StateBuilder
def test_statebuilder_add_get_custom_type():
    state_builder = StateBuilder()
    class DummyState(TypedDict):
        dummy: str
    state_builder.add_type("dummy_type", DummyState)
    with pytest.raises(ValueError, match="Registered type: dummy_type"):
        state_builder.add_type("dummy_type", DummyState)
    with pytest.raises(ValueError, match="Unregistered type: unresister_type"):
        state_builder._get_type("unresister_type")

# Test for adding and getting reducers in StateBuilder
def test_statebuilder_add_get_reducer():
    def dummy_func():
        pass
    state_builder = StateBuilder()
    state_builder.add_reducer("test", dummy_func)
    with pytest.raises(ValueError, match="Registered function: test"):
        state_builder.add_reducer("test", dummy_func)
    assert state_builder._get_reducer("test") == dummy_func
    with pytest.raises(ValueError, match="Unregistered function: unresister"):
        state_builder._get_reducer("unresister")

# Test for generating state with StateBuilder
def test_statebuilder_gen_state():
    def reduce_test(left, right):
        pass
    class DummyType(TypedDict):
        dummy: str
    class TestState(TypedDict):
        operatoradd: Annotated[list, operator.add]
        udf: Annotated[DummyType, reduce_test]
        scalar: str
    test_state = [
        {"field_name": "operatoradd", "type": "list", "reducer": "add"},
        {"field_name": "udf", "type": "DummyType", "reducer": "reduce_test"},
        {"field_name": "scalar", "type": "str"},
    ]
    state_builder = StateBuilder()
    state_builder.add_type("DummyType", DummyType)
    state_builder.add_reducer("add", operator.add)
    state_builder.add_reducer("reduce_test", reduce_test)
    state_class = state_builder.gen_state(test_state)
    assert 'operatoradd' in state_class.__annotations__
    assert state_class.__annotations__['operatoradd'].__origin__ == list
    assert state_class.__annotations__['operatoradd'].__metadata__[0] == operator.add
    assert 'udf' in state_class.__annotations__
    assert state_class.__annotations__['udf'].__origin__ == DummyType
    assert state_class.__annotations__['udf'].__metadata__[0] == reduce_test
    assert 'scalar' in state_class.__annotations__
    assert state_class.__annotations__['scalar'] == str

# Test for generating state with initial types and reducers in StateBuilder
def test_statebuilder_gen_state_init():
    def reduce_test(left, right):
        pass
    class DummyType(TypedDict):
        dummy: str
    class TestState(TypedDict):
        operatoradd: Annotated[list, operator.add]
        udf: Annotated[DummyType, reduce_test]
        scalar: str
    test_state = [
        {"field_name": "operatoradd", "type": "list", "reducer": "add"},
        {"field_name": "udf", "type": "DummyType", "reducer": "reduce_test"},
        {"field_name": "scalar", "type": "str"},
    ]
    type_list = {"DummyType": DummyType}
    reducer_list = {"add": operator.add, "reduce_test": reduce_test}
    state_builder = StateBuilder(type_list, reducer_list)
    state_class = state_builder.gen_state(test_state)
    assert 'operatoradd' in state_class.__annotations__
    assert state_class.__annotations__['operatoradd'].__origin__ == list
    assert state_class.__annotations__['operatoradd'].__metadata__[0] == operator.add
    assert 'udf' in state_class.__annotations__
    assert state_class.__annotations__['udf'].__origin__ == DummyType
    assert state_class.__annotations__['udf'].__metadata__[0] == reduce_test
    assert 'scalar' in state_class.__annotations__
    assert state_class.__annotations__['scalar'] == str