from typing import List, Dict, Union

from langgraph.graph import START,END

def convert_key(key: str):
    if key == 'START':
        return START
    if key == 'END':
        return END
    return key

def to_list_key(keys:Dict[str, Union[str, List[str]]]):
    key_list = []
    if isinstance(keys, str):
        key_list.append(convert_key(keys))
        return key_list
    
    for key in keys:
        key_list.append(convert_key(key))

    return key_list