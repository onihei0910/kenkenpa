"""
This module provides functionality to build workflows using a state graph.
It includes the `WorkFlowBuilder` class which allows adding node generators,
evaluation functions, and constructing workflows based on given settings.
"""
from typing import List, Dict, Union

from langgraph.graph import  StateGraph

from dict_to_lg_workflow.state import StateBuilder
from dict_to_lg_workflow.edges import add_static_conditional_edge
from dict_to_lg_workflow.common import convert_key

class WorkFlowBuilder():
    """
    A builder class to construct workflows using a state graph 
    based on provided settings and configuration schema.

    Attributes:
        graph_settings (dict): The settings for the graph.
        config_schema (Any): The schema for the configuration.
        node_generators (dict): A dictionary to store node generator functions.
        evaluate_functions (dict): A dictionary to store evaluation functions.
        workflow (dict): The constructed workflow.
        custom_state (Any): The custom state for the workflow.
    """
    def __init__(self,graph_settings,config_schema):
        """
        Initializes the WorkFlowBuilder with graph settings and configuration schema.

        Args:
            graph_settings (dict): The settings for the graph.
            config_schema (Any): The schema for the configuration.
        """
        self.graph_settings = graph_settings
        self.config_schema = config_schema
        self.node_generators = {}
        self.evaluete_functions = {}
        self.workflow = {}
        self.custom_state = None
        self.statebuilder = StateBuilder()

    def getworkflow(self):
        """
        Constructs and returns the workflow based on the graph settings.

        Returns:
            Any: The constructed workflow.
        """
        self.workflow = self._add_workflow(self.graph_settings)
        return self.workflow

    def add_node_generator(self,name:str,function):
        """
        Adds a node generator function to the builder.

        Args:
            name (str): The name of the node generator.
            function (Callable): The function to generate nodes.
        """
        self.node_generators[name] = function

    def add_evaluete_function(self,name:str,function):
        """
        Adds an evaluation function to the builder.

        Args:
            name (str): The name of the evaluation function.
            function (Callable): The function to evaluate conditions.
        """
        self.evaluete_functions[name] = function

    def add_reducer(self,name:str,function):
        self.statebuilder.add_reducer(name,function)

    def add_type(self,name:str,type):
        self.statebuilder.add_type(name,type)

    def _add_workflow(self,workflow_settings):
        """
        Recursively constructs a workflow based on the provided workflow settings.

        Args:
            workflow_settings (dict): The settings for the workflow.

        Returns:
            StateGraph: The constructed state graph for the workflow.
        """
        self.custom_state = self.statebuilder.gen_state(workflow_settings.get("state",[]))
        workflow = StateGraph(self.custom_state,config_schema=self.config_schema)

        for flow in workflow_settings.get("flows",[]):
            flow_workflow_type = get_workflow_type(flow)
            flow_parameter = get_flow_parameter(flow)
            metadata = get_metadata(flow)
            settings = flow.get('settings',{})

            if flow_workflow_type == "workflow":
                node_name = flow_parameter['name']
                subworkflow = self._add_workflow(flow)
                workflow.add_node(node_name,subworkflow.compile())

            elif flow_workflow_type == "node":
                node_name = flow_parameter['name']
                generator = flow_parameter['generator']
                node_func = self._gen_node(generator,metadata,settings)
                workflow.add_node(node_name,node_func)

            elif flow_workflow_type == "conditional_edge":
                start_key = flow_parameter['start_key']

                edge_function = self._add_conditional_edge(metadata,settings)
                conditions = metadata['flow_parameter']['conditions']
                
                return_types = extract_literals(conditions)
                path_map = [convert_key(type_str) for type_str in return_types]

                workflow.add_conditional_edges(
                    source = start_key,
                    path = edge_function,
                    path_map = path_map
                )

            elif flow_workflow_type == "edge":
                start_key = convert_key(flow_parameter['start_key'])
                end_key = convert_key(flow_parameter['end_key'])

                workflow.add_edge(
                    start_key = start_key,
                    end_key = end_key
                )

        return workflow

    def _gen_node(self,generator,metadata,settings):
        """
        Generates a node function using the specified generator, metadata, and settings.

        Args:
            generator (str): The name of the generator function.
            metadata (Any): The metadata for the node.
            settings (Any): The settings for the node.

        Returns:
            Callable: The generated node function.
        """
        add_agent_function = self.node_generators[generator]

        return add_agent_function(
            metadata = metadata,
            settings = settings,
            )

    def _add_conditional_edge(self,metadata,settings):
        """
        Adds a conditional edge to the workflow based on the provided metadata and settings.

        Args:
            metadata (Any): The metadata for the conditional edge.
            settings (Any): The settings for the conditional edge.

        Returns:
            Callable: The function to evaluate the conditional edge.
        """
        return add_static_conditional_edge(
            metadata = metadata,
            settings = settings,
            evaluate_functions = self.evaluete_functions
            )
    


def extract_literals(conditions: List[Dict[str, Union[Dict, str]]]) -> str:
    """
    Extracts literal values from the conditions.
    Args:
        conditions (list): A list of conditions to extract literals from.
    Returns:
        list: A list of literal values extracted from the conditions.
    """
    results = []
    for condition in conditions:
        if 'result' in condition:
            results.append(condition['result'])
        elif 'default' in condition:
            results.append(condition['default'])
    return results


def get_metadata(settings):
    """
    Retrieves the metadata from the provided settings.

    Args:
        settings (dict): The settings to retrieve metadata from.

    Returns:
        Any: The retrieved metadata.
    """
    return settings.get('metadata')

def get_workflow_type(settings):
    """
    Retrieves the workflow type from the provided settings.

    Args:
        settings (dict): The settings to retrieve the workflow type from.

    Returns:
        str: The retrieved workflow type.
    """
    metadata = get_metadata(settings)
    return metadata.get('workflow_type',"")

def get_flow_name(settings):
    """
    Retrieves the flow name from the provided settings.

    Args:
        settings (dict): The settings to retrieve the flow name from.

    Returns:
        str: The retrieved flow name.
    """
    metadata = get_metadata(settings)
    return metadata.get('name',"")

def get_flow_parameter(settings):
    """
    Retrieves the flow parameters from the provided settings.

    Args:
        settings (dict): The settings to retrieve the flow parameters from.

    Returns:
        dict: The retrieved flow parameters.
    """
    metadata = get_metadata(settings)
    return metadata.get('flow_parameter',{})



