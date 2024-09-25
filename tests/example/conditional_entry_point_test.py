"""
Experiment with the conditional entry point.
Some parts of the test code are adapted from the code at the following URL.
https://langchain-ai.github.io/langgraph/how-tos/branching/
"""

import operator
from typing import Any

from kenkenpa.builder import StateGraphBuilder


def gen_return_node_value(factory_parameter,flow_parameter):

    class ReturnNodeValue:
        def __init__(self, node_secret: str):
            self._value = node_secret

        def __call__(self, state ) -> Any:
            print(f"Adding {self._value} to {state['aggregate']}")
            return {"aggregate": [self._value]}
    
    object = ReturnNodeValue(factory_parameter['node_secret'])
    return object

graph_settings = {
    "graph_type":"stategraph",
    "flow_parameter":{
        "name":"Parallel-node",
        "state" : [ 
            {
                "field_name": "aggregate",
                "type": "list",
                "reducer":"add"
            },
            {
                "field_name": "which",
                "type": "str",
            },
        ],
    },
    "flows": [
        { # __start__ -> b,c or c,d
            "graph_type":"static_conditional_entry_point",
            "flow_parameter":{
                "conditions":[
                    {
                        "expression": {
                            "eq": [{"type": "state_value", "name": "which"}, "cd"],
                        },
                        "result": ["c","d"]
                    },
                    {"default": ["b","c"]} 
                ]
            },
        },
        { # node b
            "graph_type":"node",
            "flow_parameter": {
                "name":"b",
                "factory":"gen_return_node_value", 
            },
            "factory_parameter" : {"node_secret":"I'm B"},
        },
        { # node c
            "graph_type":"node",
            "flow_parameter": {
                "name":"c",
                "factory":"gen_return_node_value", 
            },
            "factory_parameter" : {"node_secret":"I'm C"},
        },
        { # node d
            "graph_type":"node",
            "flow_parameter": {
                "name":"d",
                "factory":"gen_return_node_value", 
            },
            "factory_parameter" : {"node_secret":"I'm D"},
        },
        { # node e
            "graph_type":"node",
            "flow_parameter": {
                "name":"e",
                "factory":"gen_return_node_value", 
            },
            "factory_parameter" : {"node_secret":"I'm E"},
        },

        { # normal_edge b,c,d -> e
            "graph_type":"edge",
            "flow_parameter": {
                "start_key":["b","c","d"],
                "end_key":"e"
            },
        },
        { # normal_edge e -> END
            "graph_type":"edge",
            "flow_parameter": {
                "start_key":"e",
                "end_key":"END"
            },
        },
    ]
}

def test_conditional_branching():
    # Generate the StateGraphBuilder from graph_settings.
    stategraph_builder = StateGraphBuilder(graph_settings)

    # Register the reducer to be used in the StateGraphBuilder.
    stategraph_builder.add_reducer("add",operator.add)

    # Register the node factory with the stategraph_builder.
    stategraph_builder.add_node_factory("gen_return_node_value",gen_return_node_value)

    # The gen_stategraph method generates a compilable StateGraph.
    stategraph = stategraph_builder.gen_stategraph()

    graph = stategraph.compile() 

    print(f"\ngraph")
    graph.get_graph().print_ascii()

    print('graph.invoke({"aggregate": [],"which":"bc"}, {"configurable": {"thread_id": "foo"}})')
    graph.invoke({"aggregate": [],"which":"bc"}, {"configurable": {"thread_id": "foo"}})

    print('graph.invoke({"aggregate": [],"which":"cd"}, {"configurable": {"thread_id": "foo"}})')
    graph.invoke({"aggregate": [],"which":"cd"}, {"configurable": {"thread_id": "foo"}})
