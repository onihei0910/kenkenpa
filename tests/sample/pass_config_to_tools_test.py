"""
How to pass config to toolsの実装例
https://langchain-ai.github.io/langgraph/how-tos/pass-config-to-tools/
"""
import operator
from typing import List

from langchain_core.tools import tool
from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages import HumanMessage

from langgraph.prebuilt import ToolNode
from langgraph.graph import  MessagesState,add_messages #TODO MessagesStateが使えない。。。
from langgraph.checkpoint.memory import MemorySaver

from langchain_openai import ChatOpenAI

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
        self.model_with_tools = ChatOpenAI(
            model="gpt-4o-mini"
        ).bind_tools(tools)

    def __call__(self,state: MessagesState):
        messages = state["messages"]
        response = self.model_with_tools.invoke(messages)
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
        {# edge START -> agent
            "graph_type":"edge",
            "flow_parameter":{
                "start_key":"START",
                "end_key":"agent"
            },
        },
        {# coditional edge 
            "graph_type":"static_conditional_edge",
            "flow_parameter":{
                "start_key":"agent",
                "conditions":[
                    {
                        "expression": {
                            "eq": [{"type": "function", "name": "is_tool_message"}, True],
                        },
                        "result": "tools"
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
    ]
}

def test_sample_pass_config_to_tools():
    # graph_settingsからStateGraphBuilderを生成します。
    stategraph_builder = StateGraphBuilder(graph_settings)

    # reducerを登録します
    stategraph_builder.add_reducer("add_messages",add_messages)

    # stategraph_builderにノードファクトリーを登録しておきます。
    stategraph_builder.add_node_factory("AgentOpenAI",AgentOpenAI)
    stategraph_builder.add_node_factory("tools_node_factory",tools_node_factory)

    # 同様に、評価関数も登録します。
    stategraph_builder.add_evaluete_function("is_tool_message", is_tool_message,)

    # gen_stategraphメソッドでコンパイル可能なStateGraphを取得できます。
    stategraph = stategraph_builder.gen_stategraph()

    # 以降はLangGraphの一般的な使用方法に従ってコードを記述します。
    memory = MemorySaver()
    app =  stategraph.compile(checkpointer=memory)

    print(f"\ngraph")
    app.get_graph().print_ascii()

    user_to_pets.clear() # Clear the state

    print(F"User information prior to run :{user_to_pets}")

    inputs = ({"messages":[HumanMessage(content="my favorite pets are cats and dogs")]})

    for output in app.stream(inputs,{"configurable": {"thread_id":42,"user_id": "123"}}):
        # stream() yields dictionaries with output keyed by node name
        for key, value in output.items():
            print(f"Output from node '{key}':")
            print("---")
            print(value)
        print("\n---\n")

    print(f"User information after the run: {user_to_pets}")

    inputs = {"messages": [HumanMessage(content="what are my favorite pets?")]}
    for output in app.stream(inputs, {"configurable": {"thread_id":42,"user_id": "123"}}):
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
    for output in app.stream(inputs, {"configurable": {"thread_id":42,"user_id": "123"}}):
        # stream() yields dictionaries with output keyed by node name
        for key, value in output.items():
            print(f"Output from node '{key}':")
            print("---")
            print(value)
        print("\n---\n")


    print(f"User information prior to run: {user_to_pets}")