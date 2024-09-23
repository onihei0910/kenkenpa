import pytest
import operator

from typing_extensions import TypedDict, Annotated 

from kenkenpa.state import StateBuilder

def test_statebuilder_type():
    test_primitive_type_list =  {
        "int":int,
        "float":float,
        "complex":complex,
        "str":str,
        "list":list,
        "tuple":tuple,
        "dict":dict,
        "set":set,
        "frozenset":frozenset,
        "bool":bool,
    }

    assert StateBuilder.primitive_type_list == test_primitive_type_list

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

    with pytest.raises(ValueError, match="Reserved type: int"):
        state_builder.add_type("int", int)

    with pytest.raises(ValueError, match="Reserved type: float"):
        state_builder.add_type("float", float)

    with pytest.raises(ValueError, match="Reserved type: complex"):
        state_builder.add_type("complex", complex)

    with pytest.raises(ValueError, match="Reserved type: str"):
        state_builder.add_type("str", str)

    with pytest.raises(ValueError, match="Reserved type: list"):
        state_builder.add_type("list", list)

    with pytest.raises(ValueError, match="Reserved type: tuple"):
        state_builder.add_type("tuple", tuple)

    with pytest.raises(ValueError, match="Reserved type: dict"):
        state_builder.add_type("dict", dict)

    with pytest.raises(ValueError, match="Reserved type: set"):
        state_builder.add_type("set", set)

    with pytest.raises(ValueError, match="Reserved type: frozenset"):
        state_builder.add_type("frozenset", frozenset)

    with pytest.raises(ValueError, match="Reserved type: bool"):
        state_builder.add_type("bool", bool)

    class DummyState(TypedDict):
        dummy:str

    state_builder.add_type("dummy_type",DummyState)
    with pytest.raises(ValueError, match="Registered type: dummy_type"):
        state_builder.add_type("dummy_type", DummyState)

    with pytest.raises(ValueError, match="Unregistered type: unresister_type"):
        state_builder._get_type("unresister_type") 

def test_statebuilder_reducer():
    def dummy_func():
        pass

    state_builder = StateBuilder()
    state_builder.add_reducer("test", dummy_func)  
    with pytest.raises(ValueError, match="Registered function: test"):
        state_builder.add_reducer("test", dummy_func)
    
    assert state_builder._get_reducer("test") == dummy_func

    with pytest.raises(ValueError, match="Unregistered function: unresister"):
        state_builder._get_reducer("unresister",)

def test_statebuilder_gen_state():
    def reduce_test(left, right):
        pass

    class DummyType(TypedDict):
        dummy:str

    class TestState(TypedDict):
        operatoradd: Annotated[list, operator.add]
        udf: Annotated[DummyType, reduce_test]
        scalar: str

    test_state = [ 
            {
                "field_name": "operatoradd",
                "type": "list",
                "reducer":"add"
            },
            {
                "field_name": "udf",
                "type": "DummyType",
                "reducer":"reduce_test"
            },
            {
                "field_name": "scalar",
                "type": "str",
            },
        ]
    
    state_builder = StateBuilder()
    state_builder.add_type("DummyType",DummyType)
    state_builder.add_reducer("add",operator.add)
    state_builder.add_reducer("reduce_test",reduce_test)

    assert 'operatoradd' in TestState.__annotations__

    assert TestState.__annotations__['operatoradd'].__origin__ == list
    assert TestState.__annotations__['operatoradd'].__metadata__[0] == operator.add

    assert 'udf' in TestState.__annotations__

    assert TestState.__annotations__['udf'].__origin__ == DummyType
    assert TestState.__annotations__['udf'].__metadata__[0] == reduce_test

    assert 'scalar' in TestState.__annotations__

    assert TestState.__annotations__['scalar'] == str

    state_class = state_builder.gen_state(test_state)
    assert 'operatoradd' in state_class.__annotations__

    assert state_class.__annotations__['operatoradd'].__origin__ == list
    assert state_class.__annotations__['operatoradd'].__metadata__[0] == operator.add

    assert 'udf' in state_class.__annotations__

    assert state_class.__annotations__['udf'].__origin__ == DummyType
    assert state_class.__annotations__['udf'].__metadata__[0] == reduce_test

    assert 'scalar' in state_class.__annotations__

    assert state_class.__annotations__['scalar'] == str

def test_statebuilder_gen_state_init():
    def reduce_test(left, right):
        pass

    class DummyType(TypedDict):
        dummy:str

    class TestState(TypedDict):
        operatoradd: Annotated[list, operator.add]
        udf: Annotated[DummyType, reduce_test]
        scalar: str

    test_state = [ 
            {
                "field_name": "operatoradd",
                "type": "list",
                "reducer":"add"
            },
            {
                "field_name": "udf",
                "type": "DummyType",
                "reducer":"reduce_test"
            },
            {
                "field_name": "scalar",
                "type": "str",
            },
        ]
    
    type_list = {
        "DummyType":DummyType
    }

    reducer_list = {
        "add":operator.add,
        "reduce_test":reduce_test,
    }
    state_builder = StateBuilder(type_list,reducer_list)

    assert 'operatoradd' in TestState.__annotations__

    assert TestState.__annotations__['operatoradd'].__origin__ == list
    assert TestState.__annotations__['operatoradd'].__metadata__[0] == operator.add

    assert 'udf' in TestState.__annotations__

    assert TestState.__annotations__['udf'].__origin__ == DummyType
    assert TestState.__annotations__['udf'].__metadata__[0] == reduce_test

    assert 'scalar' in TestState.__annotations__

    assert TestState.__annotations__['scalar'] == str

    state_class = state_builder.gen_state(test_state)
    assert 'operatoradd' in state_class.__annotations__

    assert state_class.__annotations__['operatoradd'].__origin__ == list
    assert state_class.__annotations__['operatoradd'].__metadata__[0] == operator.add

    assert 'udf' in state_class.__annotations__

    assert state_class.__annotations__['udf'].__origin__ == DummyType
    assert state_class.__annotations__['udf'].__metadata__[0] == reduce_test

    assert 'scalar' in state_class.__annotations__

    assert state_class.__annotations__['scalar'] == str


