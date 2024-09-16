from typing import List, Dict, Union, Optional, Type, Any

from langgraph.graph import  StateGraph

from kenkenpa.state import StateBuilder
from kenkenpa.edges import gen_static_conditional_edge
from kenkenpa.common import to_list_key

class StateGraphBuilder():
    def __init__(
        self,
        graph_settings:Dict,
        config_schema:Optional[Type[Any]]=None,
        node_generators:Dict=None,
        evaluete_functions:Dict=None,
        reducers:Dict=None,
        types:Dict=None,
        ):
        self.graph_settings = graph_settings
        self.config_schema = config_schema
        if node_generators:
            self.node_generators = node_generators
        else:
            self.node_generators = {}

        if evaluete_functions:
            self.evaluete_functions = evaluete_functions
        else:
            self.evaluete_functions = {}
        
        self.statebuilder = StateBuilder(types,reducers)

        self.workflow = {}
        self.custom_state = None
        

    def gen_stategraph(self):
        self.workflow = self._gen_workflow(self.graph_settings)
        return self.workflow

    def add_node_generator(self,name:str,function):
        self.node_generators[name] = function

    def add_evaluete_function(self,name:str,function):
        self.evaluete_functions[name] = function

    def add_reducer(self,name:str,function):
        self.statebuilder.add_reducer(name,function)

    def add_type(self,name:str,type):
        self.statebuilder.add_type(name,type)

    def _gen_workflow(self,workflow_settings):
        workflow_flow_parameter = workflow_settings.get("flow_parameter")
        print(workflow_flow_parameter)
        state = workflow_flow_parameter.get("state",[])

        self.custom_state = self.statebuilder.gen_state(state)
        workflow = StateGraph(self.custom_state,config_schema=self.config_schema)

        for flow in workflow_settings.get("flows",[]):
            flow_workflow_type = flow.get('workflow_type')
            flow_parameter = flow.get('flow_parameter',{})
            generator_parameter = flow.get('generator_parameter',{})

            if flow_workflow_type == "workflow":
                node_name = flow_parameter['name']
                subworkflow = self._gen_workflow(flow)
                workflow.add_node(node_name,subworkflow.compile())

            elif flow_workflow_type == "node":
                node_name = flow_parameter['name']
                generator = flow_parameter['generator']

                add_agent_function = self.node_generators[generator]

                node_func = add_agent_function(
                    generator_parameter = generator_parameter,
                    flow_parameter = flow_parameter,
                    )

                workflow.add_node(node_name,node_func)

            elif flow_workflow_type == "edge":
                validate_keys(flow_parameter['start_key'],flow_parameter['end_key'])
                
                start_key_list = to_list_key(flow_parameter['start_key'])
                end_key_list = to_list_key(flow_parameter['end_key'])
                
                for end_key in end_key_list:
                    for start_key in start_key_list:
                        workflow.add_edge(
                            start_key = start_key,
                            end_key = end_key
                        )

            elif flow_workflow_type == "static_conditional_edge":
                start_key = flow_parameter['start_key']
                conditions = flow_parameter['conditions']

                edge_function = gen_static_conditional_edge(
                    conditions = conditions,
                    evaluate_functions = self.evaluete_functions
                    )
                
                return_types = extract_literals(conditions)

                workflow.add_conditional_edges(
                    source = start_key,
                    path = edge_function,
                    path_map = return_types
                )

            elif flow_workflow_type == "static_conditional_entry_point":
                conditions = flow_parameter['conditions']

                edge_function = gen_static_conditional_edge(
                    conditions = conditions,
                    evaluate_functions = self.evaluete_functions
                    )
                
                return_types = extract_literals(conditions)

                workflow.set_conditional_entry_point(
                    path = edge_function,
                    path_map = return_types
                )
        return workflow

def extract_literals(conditions: List[Dict[str, Union[Dict, str]]]) -> str:
    results = []
    for condition in conditions:
        if 'result' in condition:
            results.extend(to_list_key(condition['result']))
        elif 'default' in condition:
            results.extend(to_list_key(condition['default']))
    return results

def validate_keys(
        start_key: Dict[str, Union[str, List[str]]],
        end_key: Dict[str, Union[str, List[str]]]
        ) -> bool:
    
    def is_valid_key(key):
        return isinstance(key, str) or (isinstance(key, list) and all(isinstance(item, str) for item in key))
    
    if not is_valid_key(start_key) or not is_valid_key(end_key):
        raise ValueError(f"start_keyとend_keyはstrかlist[str]である必要があります。\nstart_key:{start_key}\nend_key:{end_key}")
    
    start_key_is_list = isinstance(start_key, list) and len(start_key) > 1
    end_key_is_list = isinstance(end_key, list) and len(end_key) > 1
    
    if start_key_is_list and end_key_is_list:
        raise ValueError(f"start_key または end_key のいずれか一方のみが、要素が複数のリストであることができます。\nstart_key:{start_key}\nend_key:{end_key}")
    
    return True

