from typing import TypedDict
from pydantic import BaseModel
from kenkenpa.builder import StateGraphBuilder


def node_factory_a(factory_parameter,flow_parameter):
    def node_a(state):
        return 
    return node_a

def node_factory_b(factory_parameter,flow_parameter):

    def node_b(state):
        return 
    return node_b

class NodeClassA():
    def __init__(self,factory_parameter,flow_parameter):
        pass
    def __call__(self,state,config):
        return

class NodeClassB():
    def __init__(self,factory_parameter,flow_parameter):
        pass
    def __call__(self,state,config):
        return

def evaluate_fanc_a(state, config, **kwargs):
    return True

def evaluate_fanc_b(state, config, **kwargs):
    return True

def reducer_a(left,right):
    if left is None:
        left = []
    if not right:
        return []
    return left + right

def reducer_b(left,right):
    if left is None:
        left = []
    if not right:
        return []
    return left + right

class Type_A(TypedDict):
    dummy_a: str
    dummy_b: str

class Type_B(BaseModel):
    dummy_a:str
    dummy_b:str
    dummy_c:str

class ConfigSchema(TypedDict):
    dummy : str

def test_state_state_graph_init():
    factory_list = {
        "node_factory_a_key": node_factory_a,
        "node_factory_b_key": node_factory_b,
        "NodeClassA_key": NodeClassA,
        "NodeClassB_key": NodeClassB,
    }

    evaluate_func_list = {
        "evaluate_fanc_a_key": evaluate_fanc_a,
        "evaluate_fanc_b_key": evaluate_fanc_b,
    }

    reducer_list = {
        "reducer_a_key": reducer_a,
        "reducer_b_key": reducer_b,
    }

    type_list = {
        "Type_A_key": Type_A,
        "Type_B_key": Type_B,
    }

    graph_settings = {
        "graph_type":"stategraph",
        "flow_parameter":{
            "name":"builder_test",
            "state" : [ 
                {
                    "field_name": "test_field", #フィールド名
                    "type": "Type_A_key", # 型
                    "reducer":"reducer_a_key" # reducerと紐づけるキー
                },
            ],
        },
        "flows": [
            { # node A
                "graph_type":"node",
                "flow_parameter": {
                    "name":"test_node_a",
                    "factory":"node_factory_a_key", 
                },
                "factory_parameter" : {"node_secret":"I'm A"},
            },
            { # normal_edge START-> a
                "graph_type":"edge",
                "flow_parameter":{
                    "start_key":"START",
                    "end_key":"test_node_a"
                },
            },
            { # normal_edge d -> END
                "graph_type":"edge",
                "flow_parameter": {
                    "start_key":"test_node_a",
                    "end_key":"END"
                },
            },
        ]
    }

    test_builder = StateGraphBuilder(
        graph_settings = graph_settings,
        config_schema = ConfigSchema,
        node_factorys = factory_list,
        evaluete_functions = evaluate_func_list,
        reducers =  reducer_list,
        types = type_list
    )
    stategraph = test_builder.gen_stategraph()
    assert test_builder.graph_settings == graph_settings
    assert test_builder.config_schema == ConfigSchema
    assert test_builder.node_factorys == factory_list
    assert test_builder.evaluete_functions == evaluate_func_list

    state_builder = test_builder.statebuilder
    assert state_builder.reducer_list == reducer_list
    assert state_builder.type_list == type_list


    graph = stategraph.compile() 
    graph.get_graph().print_ascii()

def test_state_state_graph_add_method():

    graph_settings = {
        "graph_type":"stategraph",
        "flow_parameter":{
            "name":"builder_test",
            "state" : [ 
                {
                    "field_name": "test_field", #フィールド名
                    "type": "Type_A_key", # 型
                    "reducer":"reducer_a_key" # reducerと紐づけるキー
                },
            ],
        },
        "flows": [
            { # node A
                "graph_type":"node",
                "flow_parameter": {
                    "name":"test_node_a",
                    "factory":"node_factory_a_key", 
                },
                "factory_parameter" : {"node_secret":"I'm A"},
            },
            { # normal_edge START-> a
                "graph_type":"edge",
                "flow_parameter":{
                    "start_key":"START",
                    "end_key":"test_node_a"
                },
            },
            { # normal_edge d -> END
                "graph_type":"edge",
                "flow_parameter": {
                    "start_key":"test_node_a",
                    "end_key":"END"
                },
            },
        ]
    }

    factory_list = {
        "node_factory_a_key": node_factory_a,
        "node_factory_b_key": node_factory_b,
        "NodeClassA_key": NodeClassA,
        "NodeClassB_key": NodeClassB,
    }

    evaluate_func_list = {
        "evaluate_fanc_a_key": evaluate_fanc_a,
        "evaluate_fanc_b_key": evaluate_fanc_b,
    }

    reducer_list = {
        "reducer_a_key": reducer_a,
        "reducer_b_key": reducer_b,
    }

    type_list = {
        "Type_A_key": Type_A,
        "Type_B_key": Type_B,
    }

    test_builder = StateGraphBuilder(
        graph_settings = graph_settings,
        config_schema = ConfigSchema,
    )
    test_builder.add_node_factory("node_factory_a_key", node_factory_a)
    test_builder.add_node_factory("node_factory_b_key", node_factory_b)
    test_builder.add_node_factory("NodeClassA_key", NodeClassA)
    test_builder.add_node_factory("NodeClassB_key", NodeClassB)

    test_builder.add_evaluete_function("evaluate_fanc_a_key", evaluate_fanc_a)
    test_builder.add_evaluete_function("evaluate_fanc_b_key", evaluate_fanc_b)

    test_builder.add_reducer("reducer_a_key", reducer_a)
    test_builder.add_reducer("reducer_b_key", reducer_b)

    test_builder.add_type("Type_A_key", Type_A)
    test_builder.add_type("Type_B_key", Type_B)

    stategraph = test_builder.gen_stategraph()
    assert test_builder.graph_settings == graph_settings
    assert test_builder.config_schema == ConfigSchema
    assert test_builder.node_factorys == factory_list
    assert test_builder.evaluete_functions == evaluate_func_list

    state_builder = test_builder.statebuilder
    assert state_builder.reducer_list == reducer_list
    assert state_builder.type_list == type_list

    graph = stategraph.compile() 
    graph.get_graph().print_ascii()

def test_state_state_graph_graph_types():

    sub_graph_a_settings = {
        "graph_type":"stategraph",
        "flow_parameter":{
            "name":"subgraph_a",
            "state" : [ 
                {
                    "field_name": "test_field", #フィールド名
                    "type": "Type_A_key", # 型
                    "reducer":"reducer_a_key" # reducerと紐づけるキー
                },
            ],
        },
        "flows": [
            { # node A
                "graph_type":"node",
                "flow_parameter": {
                    "name":"test_node_a",
                    "factory":"NodeClassA_key", 
                },
                "factory_parameter" : {"node_secret":"I'm A"},
            },
            { # normal_edge START-> a
                "graph_type":"edge",
                "flow_parameter":{
                    "start_key":"START",
                    "end_key":"test_node_a"
                },
            },
            { # normal_edge d -> END
                "graph_type":"edge",
                "flow_parameter": {
                    "start_key":"test_node_a",
                    "end_key":"END"
                },
            },
        ]
    }

    sub_graph_b_settings = {
        "graph_type":"stategraph",
        "flow_parameter":{
            "name":"subgraph_b",
            "state" : [ 
                {
                    "field_name": "test_field", #フィールド名
                    "type": "Type_A_key", # 型
                    "reducer":"reducer_a_key" # reducerと紐づけるキー
                },
                {
                    "field_name": "test_field_b", #フィールド名
                    "type": "Type_B_key", # 型
                    "reducer":"reducer_a_key" # reducerと紐づけるキー
                },
            ],
        },
        "flows": [
            { # node A
                "graph_type":"node",
                "flow_parameter": {
                    "name":"test_node_a",
                    "factory":"NodeClassA_key", 
                },
                "factory_parameter" : {"node_secret":"I'm A"},
            },
            { # node B
                "graph_type":"node",
                "flow_parameter": {
                    "name":"test_node_b",
                    "factory":"NodeClassB_key", 
                },
                "factory_parameter" : {"node_secret":"I'm B"},
            },
            { # normal_edge START-> a
                "graph_type":"edge",
                "flow_parameter":{
                    "start_key":"START",
                    "end_key":"test_node_a"
                },
            },
            {# 静的条件付きエッジ
                "graph_type":"static_conditional_edge",
                "flow_parameter":{
                    "start_key":"test_node_a",
                    "conditions":[
                        {
                            "expression": {
                                "eq": [{"type": "state_value", "name": "test_field_b"}, "testvalue"],
                            },
                            "result": "test_node_b"
                        },
                        {"default": "END"} 
                    ]
                },
            },
            { # normal_edge d -> END
                "graph_type":"edge",
                "flow_parameter": {
                    "start_key":"test_node_b",
                    "end_key":"test_node_a"
                },
            },
        ]
    }

    parent_graph_settings = {
        "graph_type":"stategraph",
        "flow_parameter":{
            "name":"parent_graph",
            "state" : [ 
                {
                    "field_name": "test_field", #フィールド名
                    "type": "Type_A_key", # 型
                    "reducer":"reducer_a_key" # reducerと紐づけるキー
                },
            ],
        },
        "flows": [
            sub_graph_a_settings,
            sub_graph_b_settings,
            {# 静的条件付きエントリーポイント
                "graph_type":"static_conditional_entry_point",
                "flow_parameter":{
                    "conditions":[
                        {
                            "expression": {
                                "eq": [{"type": "state_value", "name": "test_field_b"}, "testvalue"],
                            },
                            "result": "subgraph_a"
                        },
                        {"default": "subgraph_b"} 
                    ]
                },
            },
            { # node C
                "graph_type":"node",
                "flow_parameter": {
                    "name":"test_node_c",
                    "factory":"NodeClassA_key", 
                },
                "factory_parameter" : {"node_secret":"I'm C"},
            },
            { # normal_edge [subgraph_a,subgraph_b] -> test_node_c
                "graph_type":"edge",
                "flow_parameter": {
                    "start_key":["subgraph_a","subgraph_b"],
                    "end_key":"test_node_c"
                },
            },
            { # normal_edge c -> END
                "graph_type":"edge",
                "flow_parameter": {
                    "start_key":"test_node_c",
                    "end_key":"END"
                },
            },
        ]
    }
    test_builder = StateGraphBuilder(
        graph_settings = parent_graph_settings,
        config_schema = ConfigSchema,
    )

    test_builder.add_node_factory("node_factory_a_key", node_factory_a)
    test_builder.add_node_factory("node_factory_b_key", node_factory_b)
    test_builder.add_node_factory("NodeClassA_key", NodeClassA)
    test_builder.add_node_factory("NodeClassB_key", NodeClassB)

    test_builder.add_evaluete_function("evaluate_fanc_a_key", evaluate_fanc_a)
    test_builder.add_evaluete_function("evaluate_fanc_b_key", evaluate_fanc_b)

    test_builder.add_reducer("reducer_a_key", reducer_a)
    test_builder.add_reducer("reducer_b_key", reducer_b)

    test_builder.add_type("Type_A_key", Type_A)
    test_builder.add_type("Type_B_key", Type_B)

    stategraph = test_builder.gen_stategraph()

    graph = stategraph.compile() 
    graph.get_graph().print_ascii()