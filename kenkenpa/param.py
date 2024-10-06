"""
This module defines a set of parameters for different graph components
and provides a function to retrieve these parameters based on a specified type.
The parameters include configurations for state graphs, nodes, edges,
and conditional logic used in graph processing.
"""
from typing import Dict

param = {}
param['stategraph'] = {
    "graph_type":"stategraph",
    "flow_parameter": {
        "name": "stategraph_name",
        "state": [],
    },
    "flows": []
}

param['state'] = {
    "field_name": "field_name",
    "type": "type",
    "reducer":"reducer"
}

param['node'] = {
    "graph_type":"node",
    "flow_parameter": {
        "name":"node_name",
        "factory":"factory_name",
    },
    "factory_parameter" : {},
}

param['edge'] = {
    "graph_type":"edge",
    "flow_parameter":{
        "start_key":"start_key",
        "end_key":"end_key"
    },
}

param['conditional_edge'] = {
    "graph_type":"configurable_conditional_edge",
    "flow_parameter":{
        "start_key":"start_key",
        "path_map":[],
        "conditions":[]
    },
}

param['conditional_entry_point'] = {
    "graph_type":"configurable_conditional_entry_point",
    "flow_parameter":{
        "path_map":[],
        "conditions":[]
    },
}

param['condition_expression'] = {
    "expression": {},
    "result": "node_name"
}

param['condition_default'] = {"default": "next_node"}

param['operater_and'] = {"and": []}
param['operater_or'] = {"or":[]}
param['operater_not'] = {"not":{}}

param['operater_eq'] = {"eq": []}
param['operater_neq'] = {"neq": []}
param['operater_gt'] = {"gt": []}
param['operater_gte'] = {"gte": []}
param['operater_lt'] = {"lt": []}
param['operater_lte'] = {"lte": []}

param['operand_function'] = {
    "type":"function",
    "name":"test_function",
    "args":{"args_key":"args_value"}
}
param['operand_state_value'] = {"type":"state_value", "name":"test_state_key"}
param['operand_config_value'] = {"type":"config_value", "name":"test_config_key"}

def create_parameter(param_type:str) -> Dict:
    """
    Retrieve the parameter configuration for a specified type.

    Args:
        param_type (str): The type of parameter to retrieve.
            This should be one of the predefined keys in the `param` dictionary.
            Valid param_type values are as follows:
            - stategraph
            - state
            - node
            - edge
            - conditional_edge
            - conditional_entry_point
            - condition_expression
            - condition_default
            - operater_and
            - operater_or
            - operater_not
            - operater_eq
            - operater_neq
            - operater_gt
            - operater_gte
            - operater_lt
            - operater_lte
            - operand_function
            - operand_state_value
            - operand_config_value

    Returns:
        Dict: The parameter configuration corresponding to the specified type.

    Raises:
        KeyError: If the specified `param_type` is not a valid key in the `param` dictionary.
    """
    try:
        return param[param_type]
    except KeyError as e:
        raise KeyError(f"Invalid key: '{param_type}'") from e
