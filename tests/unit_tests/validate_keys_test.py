import pytest
from kenkenpa.builder import validate_keys

def test_validate_keys():
    assert validate_keys("keyA","Key_B") == True
    assert validate_keys("keyA",["Key_B","Key_C"]) == True
    assert validate_keys(["Key_B","Key_C"],"keyA") == True

    exc_info = pytest.raises(ValueError, validate_keys,100,"Key_B" )
    assert str(exc_info.value) == "start_keyとend_keyはstrかlist[str]である必要があります。\nstart_key:100\nend_key:Key_B"

    exc_info = pytest.raises(ValueError, validate_keys,"keyA",100 )
    assert str(exc_info.value) == "start_keyとend_keyはstrかlist[str]である必要があります。\nstart_key:keyA\nend_key:100"

    exc_info = pytest.raises(ValueError, validate_keys,100,100 )
    assert str(exc_info.value) == "start_keyとend_keyはstrかlist[str]である必要があります。\nstart_key:100\nend_key:100"

    exc_info = pytest.raises(ValueError, validate_keys,["keyA","keyB"],["keyC","keyD"]  )
    assert str(exc_info.value) == "start_key または end_key のいずれか一方のみが、要素が複数のリストであることができます。\nstart_key:[\'keyA\', \'keyB\']\nend_key:[\'keyC\', \'keyD\']"
