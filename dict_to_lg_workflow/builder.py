"""
This module provides functionality to build workflows using a state graph.
It includes the `WorkFlowBuilder` class which allows adding node generators,
evaluation functions, and constructing workflows based on given settings.
"""
import types
from typing import Annotated,  Any, List

from langchain_core.messages import AnyMessage
from langchain_core.pydantic_v1 import BaseModel, Field

from langgraph.graph import START,END
from langgraph.graph import  StateGraph, add_messages

from dict_to_lg_workflow.edges import add_static_conditional_edge

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

    def getworkflow(self):
        """
        Constructs and returns the workflow based on the graph settings.

        Returns:
            Any: The constructed workflow.
        """
        workflow = self.graph_settings.get("workflows")
        self.workflow = self._add_workflow(workflow)
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

    def _add_workflow(self,workflow_settings):
        """
        Recursively constructs a workflow based on the provided workflow settings.

        Args:
            workflow_settings (dict): The settings for the workflow.

        Returns:
            StateGraph: The constructed state graph for the workflow.
        """
        self.custom_state = create_custom_state(workflow_settings.get("state",[]))
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

                workflow.add_conditional_edges(
                    source = start_key,
                    path = edge_function,
                )

            elif flow_workflow_type == "edge":
                start_key = check_edge(flow_parameter['start_key'])
                end_key = check_edge(flow_parameter['end_key'])

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

def check_edge(point:str):
    """
    Checks and returns the appropriate edge constant for the given point.

    Args:
        point (str): The point to check.

    Returns:
        str: The corresponding edge constant.
    """
    if point == 'START':
        return START
    if point == 'END':
        return END
    return point

def create_custom_state(params):
    """
    Factory function to create a CustomState class with custom defaults and descriptions.

    Args:
        params (List[Dict[str, Any]]): A list of dictionaries containing settings for each field.

    Returns:
        Type[BaseModel]: The created custom state class.
    """
    # アノテーション用の辞書を作成
    annotations = {
        param['field_name']: str if param['type'] == 'str' else int
        for param in params
    }
    annotations['messages'] = Annotated[list[AnyMessage], add_messages]

    fields = {
        param['field_name']: Field(default=param['default'], description=param['description'])
        for param in params
    }

    # 各フィールドのデフォルト値と説明を保存
    field_info = {
        param['field_name']: {'default': param['default'], 'description': param['description']}
        for param in params
    }

    # コンストラクタでデフォルト値を初期化
    def __init__(self, **kwargs):
        for field in self.__annotations__:
            kwargs[field] = kwargs.get(field) or field_info[field]['default']

        super(self.__class__, self).__init__(**kwargs)

    # クラスの追加メソッドを定義
    def get(self, key: str, default: List[Any] = None) -> Any:
        return getattr(self, key, default)

    new_class = types.new_class(
        'CustomState',
        (BaseModel,),
        exec_body=lambda ns: ns.update({
            '__annotations__': annotations,
            **fields,
            'get': get,
            '__init__': __init__
        })
    )
    return new_class
