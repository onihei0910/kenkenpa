"""
This module provides utility functions for converting keys and generating lists of keys.
It includes functions to convert specific string keys to predefined constants and to convert
a dictionary of keys into a list of keys.
"""
from typing import List, Dict, Union

from langgraph.graph import START,END

def convert_key(key: str):
    """
    Converts a string key to a predefined constant if it matches 'START' or 'END'.

    Args:
        key (str): The key to convert.

    Returns:
        str: The converted key.
    """
    if key == 'START':
        return START
    if key == 'END':
        return END
    return key

def to_list_key(keys:Dict[str, Union[str, List[str]]]):
    """
    Converts a key or a dictionary of keys into a list of keys.

    Args:
        keys (Dict[str, Union[str, List[str]]]): The key(s) to convert.

    Returns:
        List[str]: A list of converted keys.
    """
    key_list = []
    if isinstance(keys, str):
        key_list.append(convert_key(keys))
        return key_list

    for key in keys:
        key_list.append(convert_key(key))

    return key_list
