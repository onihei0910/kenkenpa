import pytest
import operator

from typing_extensions import TypedDict, Annotated 

from kenkenpa.edges import StaticConditionalHandler
from kenkenpa.edges import compare_values

class DummyType(TypedDict):
    dummy:str

def test_conpare_values():
    assert compare_values("==",5,5) == True
    assert compare_values("==",5,4) == False
    assert compare_values("==","aaa","aaa") == True
    assert compare_values("==","aaa","aaba") == False
    assert compare_values("equals",5,5) == True
    assert compare_values("equals",5,4) == False
    assert compare_values("equals","aaa","aaa") == True
    assert compare_values("equals","aaa","aaba") == False
    assert compare_values("eq",5,5) == True
    assert compare_values("eq",5,4) == False
    assert compare_values("eq","aaa","aaa") == True
    assert compare_values("eq","aaa","aaba") == False

    assert compare_values("!=",5,5) == False
    assert compare_values("!=",5,4) == True
    assert compare_values("!=","aaa","aaa") == False
    assert compare_values("!=","aaa","aaba") == True
    assert compare_values("not_equals",5,5) == False
    assert compare_values("not_equals",5,4) == True
    assert compare_values("not_equals","aaa","aaa") == False
    assert compare_values("not_equals","aaa","aaba") == True
    assert compare_values("neq",5,5) == False
    assert compare_values("neq",5,4) == True
    assert compare_values("neq","aaa","aaa") == False
    assert compare_values("neq","aaa","aaba") == True

    assert compare_values(">",10,9)  == True
    assert compare_values(">",10,10)  == False
    assert compare_values(">","B","A")  == True
    assert compare_values(">","B","B")  == False
    assert compare_values("greater_than",10,9)  == True
    assert compare_values("greater_than",10,10)  == False
    assert compare_values("greater_than","B","A")  == True
    assert compare_values("greater_than","B","B")  == False
    assert compare_values("gt",10,9)  == True
    assert compare_values("gt",10,10)  == False
    assert compare_values("gt","B","A")  == True
    assert compare_values("gt","B","B")  == False

    assert compare_values(">=",10,9) == True
    assert compare_values(">=",10,10) == True
    assert compare_values(">=",10,11) == False
    assert compare_values(">=","B","A") == True
    assert compare_values(">=","B","B") == True
    assert compare_values(">=","B","C") == False
    assert compare_values("greater_than_or_equals",10,9) == True
    assert compare_values("greater_than_or_equals",10,10) == True
    assert compare_values("greater_than_or_equals",10,11) == False
    assert compare_values("greater_than_or_equals","B","A") == True
    assert compare_values("greater_than_or_equals","B","B") == True
    assert compare_values("greater_than_or_equals","B","C") == False    
    assert compare_values("gte",10,9) == True
    assert compare_values("gte",10,10) == True
    assert compare_values("gte",10,11) == False
    assert compare_values("gte","B","A") == True
    assert compare_values("gte","B","B") == True
    assert compare_values("gte","B","C") == False

    assert compare_values("<",9,10)  == True
    assert compare_values("<",10,10)  == False
    assert compare_values("<","A","B")  == True
    assert compare_values("<","B","B")  == False
    assert compare_values("less_than",9,10)  == True
    assert compare_values("less_than",10,10)  == False
    assert compare_values("less_than","A","B")  == True
    assert compare_values("less_than","B","B")  == False
    assert compare_values("lt",9,10)  == True
    assert compare_values("lt",10,10)  == False
    assert compare_values("lt","A","B")  == True
    assert compare_values("lt","B","B")  == False

    assert compare_values("<=",9,10) == True
    assert compare_values("<=",10,10) == True
    assert compare_values("<=",11,10) == False
    assert compare_values("<=","A","B") == True
    assert compare_values("<=","B","B") == True
    assert compare_values("<=","C","B") == False
    assert compare_values("less_than_or_equals",9,10) == True
    assert compare_values("less_than_or_equals",10,10) == True
    assert compare_values("less_than_or_equals",11,10) == False
    assert compare_values("less_than_or_equals","A","B") == True
    assert compare_values("less_than_or_equals","B","B") == True
    assert compare_values("less_than_or_equals","C","B") == False    
    assert compare_values("lte",9,10) == True
    assert compare_values("lte",10,10) == True
    assert compare_values("lte",11,10) == False
    assert compare_values("lte","A","B") == True
    assert compare_values("lte","B","B") == True
    assert compare_values("lte","C","B") == False

    exc_info = pytest.raises(ValueError, compare_values, "int", 1,1)
    assert str(exc_info.value) == "サポートされていない比較演算子: int"