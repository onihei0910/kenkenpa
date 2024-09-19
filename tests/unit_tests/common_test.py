from kenkenpa.common import convert_key
from kenkenpa.common import to_list_key

def test_convert_key():
    assert convert_key('START') == '__start__'
    assert convert_key('END') == '__end__'
    assert convert_key('any_key') == 'any_key'

def test_to_list_key():
    assert to_list_key('any_key') == ['any_key']
    assert to_list_key(['any_key']) == ['any_key']
    assert to_list_key(['START','any_key','END']) == ['__start__','any_key','__end__']