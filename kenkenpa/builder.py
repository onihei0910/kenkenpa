"""
This module provides a StateGraphBuilder class for constructing state graphs based on provided settings.
It includes methods for adding nodes, edges, and conditional edges, as well as for generating the state graph.
"""
from typing import List, Dict, Union, Optional, Type, Any

from langgraph.graph import  StateGraph

from kenkenpa.models.stategraph import KStateGraph
from kenkenpa.models.node import KNode
from kenkenpa.models.edge import KEdge
from kenkenpa.models.static_conditional_edge import KStaticConditionalEdge
from kenkenpa.models.static_conditional_entry_point import KStaticConditionalEntoryPoint

from kenkenpa.state import StateBuilder
from kenkenpa.edges import gen_static_conditional_edge
from kenkenpa.common import to_list_key

class StateGraphBuilder():
    """
    StateGraphBuilder is responsible for constructing a state graph based on provided settings.

    Attributes:
        graph_settings (Dict): The settings for the state graph.
        config_schema (Optional[Type[Any]]): The schema for configuration.
        node_factorys (Dict): A dictionary of node factory functions.
        evaluete_functions (Dict): A dictionary of evaluation functions.
        statebuilder (StateBuilder): An instance of StateBuilder for managing state.
        stategraph (Dict): The constructed state graph.
        custom_state (Any): The custom state generated for the graph.
    """
    def __init__(
        self,
        graph_settings:Dict,
        config_schema:Optional[Type[Any]]=None,
        node_factorys:Dict=None,
        evaluete_functions:Dict=None,
        reducers:Dict=None,
        types:Dict=None,
        ):
        """
        Initializes the StateGraphBuilder with provided settings, configuration schema, node factories, evaluation functions, reducers, and types.

        Args:
            graph_settings (Dict): The settings for the state graph.
            config_schema (Optional[Type[Any]]): The schema for configuration.
            node_factorys (Dict, optional): A dictionary of node factory functions. Defaults to an empty dictionary.
            evaluete_functions (Dict, optional): A dictionary of evaluation functions. Defaults to an empty dictionary.
            reducers (Dict, optional): A dictionary of reducers. Defaults to None.
            types (Dict, optional): A dictionary of custom types. Defaults to None.
        """
        self.graph_settings = graph_settings
        self.config_schema = config_schema

        if node_factorys:
            self.node_factorys = node_factorys
        else:
            self.node_factorys = {}

        if evaluete_functions:
            self.evaluete_functions = evaluete_functions
        else:
            self.evaluete_functions = {}
        
        self.statebuilder = StateBuilder(types,reducers)

        self.stategraph = {}
        self.custom_state = None
        
    def gen_stategraph(self):
        """
        Generates the state graph based on the provided settings.

        Returns:
            Dict: The constructed state graph.
        """
        self.stategraph = self._gen_stategraph(self.graph_settings)
        return self.stategraph

    def add_node_factory(self,name:str,function):
        """
        Adds a node factory function to the builder.

        Args:
            name (str): The name of the node factory.
            function (callable): The node factory function to add.
        """
        self.node_factorys[name] = function

    def add_evaluete_function(self,name:str,function):
        """
        Adds an evaluation function to the builder.

        Args:
            name (str): The name of the evaluation function.
            function (callable): The evaluation function to add.
        """
        self.evaluete_functions[name] = function

    def add_reducer(self,name:str,function):
        """
        Adds a reducer function to the state builder.

        Args:
            name (str): The name of the reducer function.
            function (callable): The reducer function to add.
        """
        self.statebuilder.add_reducer(name,function)

    def add_type(self,name:str,type):
        """
        Adds a custom type to the state builder.

        Args:
            name (str): The name of the custom type.
            type_ (type): The custom type to add.
        """
        self.statebuilder.add_type(name,type)

    def _gen_stategraph(self,stategraph_settings):
        """
        Generates the state graph based on the provided settings.

        Args:
            stategraph_settings (Dict): The settings for the state graph.

        Returns:
            StateGraph: The constructed state graph.
        """
        # validate
        validate_state_graph(stategraph_settings)

        stategraph_flow_parameter = stategraph_settings.get("flow_parameter")
        state = stategraph_flow_parameter.get("state",[])

        self.custom_state = self.statebuilder.gen_state(state)
        stategraph = StateGraph(self.custom_state,config_schema=self.config_schema)

        for flow in stategraph_settings.get("flows",[]):
            graph_type = flow.get('graph_type')

            if graph_type == "stategraph":
                self._add_stategraph(stategraph,flow)

            elif graph_type == "node":
                self._add_node(stategraph,flow)

            elif graph_type == "edge":
                self._add_edge(stategraph,flow)

            elif graph_type == "static_conditional_edge":
                self._add_static_conditional_edge(stategraph,flow)

            elif graph_type == "static_conditional_entry_point":
                self._add_static_conditional_entry_point(stategraph,flow)

        return stategraph

    def _add_stategraph(self,stategraph,flow: KStateGraph):
        """
        Adds a sub-state graph to the main state graph.

        Args:
            stategraph (StateGraph): The main state graph.
            flow (KStateGraph): The sub-state graph to add.
        """
        flow_parameter = flow.get('flow_parameter',{})
        node_name = flow_parameter['name']
        substategraph = self._gen_stategraph(flow)
        stategraph.add_node(node_name,substategraph.compile())

    def _add_node(self,stategraph,flow: KNode):
        """
        Adds a node to the state graph.

        Args:
            stategraph (StateGraph): The state graph.
            flow (KNode): The node to add.
        """
        flow_parameter = flow.get('flow_parameter',{})
        factory_parameter = flow.get('factory_parameter',{})
        node_name = flow_parameter['name']
        factory = flow_parameter['factory']

        add_agent_function = self.node_factorys[factory]

        node_func = add_agent_function(
            factory_parameter = factory_parameter,
            flow_parameter = flow_parameter,
            )

        stategraph.add_node(node_name,node_func)
    
    def _add_edge(self,stategraph,flow: KEdge):
        """
        Adds an edge to the state graph.

        Args:
            stategraph (StateGraph): The state graph.
            flow (KEdge): The edge to add.
        """
        flow_parameter = flow.get('flow_parameter',{})
        
        start_key_list = to_list_key(flow_parameter['start_key'])
        end_key_list = to_list_key(flow_parameter['end_key'])
        
        for end_key in end_key_list:
            for start_key in start_key_list:
                stategraph.add_edge(
                    start_key = start_key,
                    end_key = end_key
                )

    def _add_static_conditional_edge(self,stategraph,flow:KStaticConditionalEdge):
        """
        Adds a static conditional edge to the state graph.

        Args:
            stategraph (StateGraph): The state graph.
            flow (KStaticConditionalEdge): The static conditional edge to add.
        """
        flow_parameter = flow.get('flow_parameter',{})
        start_key = flow_parameter['start_key']
        conditions = flow_parameter['conditions']

        edge_function = gen_static_conditional_edge(
            conditions = conditions,
            evaluate_functions = self.evaluete_functions
            )
        
        return_types = extract_literals(conditions)

        stategraph.add_conditional_edges(
            source = start_key,
            path = edge_function,
            #path_map = return_types
        )

    def _add_static_conditional_entry_point(self,stategraph,flow: KStaticConditionalEntoryPoint):
        """
        Adds a static conditional entry point to the state graph.

        Args:
            stategraph (StateGraph): The state graph.
            flow (KStaticConditionalEntoryPoint): The static conditional entry point to add.
        """
        flow_parameter = flow.get('flow_parameter',{})
        conditions = flow_parameter['conditions']

        edge_function = gen_static_conditional_edge(
            conditions = conditions,
            evaluate_functions = self.evaluete_functions
            )
        
        return_types = extract_literals(conditions)

        stategraph.set_conditional_entry_point(
            path = edge_function,
            path_map = return_types
        )

def extract_literals(conditions: List[Dict[str, Union[Dict, str]]]) -> str:
    """
    Extracts literals from the conditions.

    Args:
        conditions (List[Dict[str, Union[Dict, str]]]): The conditions to extract literals from.

    Returns:
        List[str]: A list of extracted literals.
    """
    results = []
    for condition in conditions:
        if 'result' in condition:
            results.extend(to_list_key(condition['result']))
        elif 'default' in condition:
            results.extend(to_list_key(condition['default']))
    return results

def validate_state_graph(values) -> bool :
    """
    Validates the state graph settings.

    Args:
        values (Dict): The state graph settings to validate.

    Returns:
        bool: True if the settings are valid, False otherwise.
    """
    KStateGraph(**values)
    return True
