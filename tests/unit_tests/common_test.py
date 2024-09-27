from kenkenpa.common import convert_key, to_list_key

def test_convert_key_start():
    assert convert_key('START') == '__start__'

def test_convert_key_end():
    assert convert_key('END') == '__end__'

def test_convert_key_any_key():
    assert convert_key('any_key') == 'any_key'

def test_to_list_key_single_string():
    assert to_list_key('any_key') == ['any_key']

def test_to_list_key_single_list():
    assert to_list_key(['any_key']) == ['any_key']

def test_to_list_key_mixed_list():
    assert to_list_key(['START', 'any_key', 'END']) == ['__start__', 'any_key', '__end__']