"""
Implementation example of how to pass config to tools and experiment with config_value
Some parts of the test code reuse the code described in the following URL.
https://langchain-ai.github.io/langgraph/how-tos/pass-config-to-tools/
"""
import operator
from typing import List

from langchain_core.tools import tool
from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages import HumanMessage,ToolMessage,AIMessage

from langgraph.prebuilt import ToolNode
from langgraph.graph import  MessagesState,add_messages
from langgraph.checkpoint.memory import MemorySaver

#from langchain_openai import ChatOpenAI

from kenkenpa.builder import StateGraphBuilder

user_to_pets = {}

@tool(parse_docstring=True)
def update_favorite_pets(
    pets: List[str],
    config: RunnableConfig,
) -> str:
    """Add the list of favorite pets.

    Args:
        pets: List of favorite pets to set.
    """
    user_id = config.get("configurable",{}).get("user_id")
    user_to_pets[user_id] = pets

    return "OK"

@tool
def delete_favorite_pets(config: RunnableConfig) -> str:
    """Delete the list of favorite pets."""
    user_id = config.get("configurable",{}).get("user_id")
    if user_id in user_to_pets:
        del user_to_pets[user_id]

    return "OK"

@tool
def list_favorite_pets(config: RunnableConfig) -> str:
    """List favorite pets if any."""
    user_id = config.get("configurable",{}).get("user_id")
    return ", ".join(user_to_pets.get(user_id,[]))

def tools_node_factory(factory_parameter,flow_parameter):
    """Generate tools node"""
    tools = [update_favorite_pets, delete_favorite_pets, list_favorite_pets]
    return ToolNode(tools)

class AgentOpenAI():
    def __init__(self,factory_parameter,flow_parameter):
        tools = [update_favorite_pets, delete_favorite_pets, list_favorite_pets]
        #self.model_with_tools = ChatOpenAI(
        #    model="gpt-4o-mini"
        #).bind_tools(tools)

    def __call__(self,state: MessagesState):
        messages = state["messages"]
        #response = self.model_with_tools.invoke(messages)
        # dummy
        response = AIMessage(content='This is dummy message')
        return {"messages": [response]}

class Maintenance():
    def __init__(self,factory_parameter,flow_parameter):
        pass

    def __call__(self,state: MessagesState):
        """System under maintenance"""
        messages = state["messages"]
        last_message = messages[-1]
        additional_kwargs = last_message.additional_kwargs
        call_id = additional_kwargs.get("tool_calls")[0].get("id")
        response = ToolMessage(content='The system is currently under maintenance.',tool_call_id=call_id)
        return {"messages": [response]}

def is_tool_message(state:MessagesState,config,**kwargs):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return True
    return False

graph_settings = {
    "graph_type":"stategraph",
    "flow_parameter":{
        "name":"React-Agent",
        "state" : [
            {
                "field_name": "messages",
                "type": "list",
                "reducer":"add_messages"
            },
        ],
    },
    "flows":[
        { # agent node
            "graph_type":"node",
            "flow_parameter":{
                "name":"agent",
                "factory":"AgentOpenAI",
            }
        },
        { # tools node
            "graph_type":"node",
            "flow_parameter":{
                "name":"tools",
                "factory":"tools_node_factory",
            }
        },
        { # Maintenance node
            "graph_type":"node",
            "flow_parameter":{
                "name":"Maintenance",
                "factory":"Maintenance",
            }
        },
        {# edge START -> agent
            "graph_type":"edge",
            "flow_parameter":{
                "start_key":"START",
                "end_key":"agent"
            },
        },
        {# coditional edge
            "graph_type":"configurable_conditional_edge",
            "flow_parameter":{
                "start_key":"agent",
                "conditions":[
                    {
                        "expression": {
                            "and":[
                                {"eq": [{"type": "function", "name": "is_tool_message"}, True]},
                                {"eq": [{"type": "config_value", "name":"tool_permission"}, True]}
                                ]
                        },
                        "result": "tools"
                    },
                    {
                        "expression": {
                            "and":[
                                {"eq": [{"type": "function", "name": "is_tool_message"}, True]},
                                {"eq": [{"type": "config_value", "name":"tool_permission"}, False]}
                                ]
                        },
                        "result": "Maintenance"
                    },
                    {"default": "END"}
                ]
            },
        },
        {# edge tools -> agent
            "graph_type":"edge",
            "flow_parameter":{
                "start_key":"tools",
                "end_key":"agent"
            },
        },
        {# edge Maintenance -> agent
            "graph_type":"edge",
            "flow_parameter":{
                "start_key":"Maintenance",
                "end_key":"agent"
            },
        },
    ]
}

def test_sample_pass_config_to_tools():
    # Generate the StateGraphBuilder from graph_settings.
    stategraph_builder = StateGraphBuilder(graph_settings)

    # Register the reducer to be used in the StateGraphBuilder.
    stategraph_builder.add_reducer("add_messages",add_messages)

    # Register the node factory with the stategraph_builder.
    stategraph_builder.add_node_factory("AgentOpenAI",AgentOpenAI)
    stategraph_builder.add_node_factory("tools_node_factory",tools_node_factory)
    stategraph_builder.add_node_factory("Maintenance",Maintenance)

    # Similarly, the evaluation function is also registered.
    stategraph_builder.add_evaluete_function("is_tool_message", is_tool_message,)

    # The gen_stategraph method generates a compilable StateGraph.
    stategraph = stategraph_builder.gen_stategraph()

    # From here on, we will write the code following the general usage of LangGraph.
    memory = MemorySaver()
    app =  stategraph.compile(checkpointer=memory)

    print(f"\ngraph")
    app.get_graph().print_ascii()

    user_to_pets.clear() # Clear the state

    print(f"User information prior to run :{user_to_pets}")

    config = {
        "configurable": {
            "thread_id":42,
            "user_id": "123",
            "tool_permission": True
        }
    }

    inputs = ({"messages":[HumanMessage(content="my favorite pets are cats and dogs")]})

    for output in app.stream(inputs,config):
        # stream() yields dictionaries with output keyed by node name
        for key, value in output.items():
            print(f"Output from node '{key}':")
            print("---")
            print(value)
        print("\n---\n")

    print(f"User information after the run: {user_to_pets}")

    inputs = {"messages": [HumanMessage(content="what are my favorite pets?")]}
    for output in app.stream(inputs,config):
        # stream() yields dictionaries with output keyed by node name
        for key, value in output.items():
            print(f"Output from node '{key}':")
            print("---")
            print(value)
        print("\n---\n")


    print(f"User information after the run: {user_to_pets}")

    inputs = {
        "messages": [
            HumanMessage(content="please forget what i told you about my favorite animals")
        ]
    }
    for output in app.stream(inputs, config):
        # stream() yields dictionaries with output keyed by node name
        for key, value in output.items():
            print(f"Output from node '{key}':")
            print("---")
            print(value)
        print("\n---\n")


    print(f"User information after the run: {user_to_pets}")


    config = {
        "configurable": {
            "thread_id":42,
            "user_id": "123",
            "tool_permission": False
        }
    }

    inputs = ({"messages":[HumanMessage(content="my favorite pets are cats and dogs")]})

    for output in app.stream(inputs,config):
        # stream() yields dictionaries with output keyed by node name
        for key, value in output.items():
            print(f"Output from node '{key}':")
            print("---")
            print(value)
        print("\n---\n")

    print(f"User information after the run: {user_to_pets}")

    inputs = {"messages": [HumanMessage(content="what are my favorite pets?")]}
    for output in app.stream(inputs,config):
        # stream() yields dictionaries with output keyed by node name
        for key, value in output.items():
            print(f"Output from node '{key}':")
            print("---")
            print(value)
        print("\n---\n")


    print(f"User information after the run: {user_to_pets}")

    inputs = {
        "messages": [
            HumanMessage(content="please forget what i told you about my favorite animals")
        ]
    }
    for output in app.stream(inputs, config):
        # stream() yields dictionaries with output keyed by node name
        for key, value in output.items():
            print(f"Output from node '{key}':")
            print("---")
            print(value)
        print("\n---\n")


    print(f"User information prior to run: {user_to_pets}")