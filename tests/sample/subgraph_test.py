"""
このテストでは、サブグラフの設定方法を説明します。
react_agent_test.pyで説明したreact-agentをサブグラフとして設定します。
"""
from langchain_core.messages import HumanMessage
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.tools import tool
from langchain_core.messages import AnyMessage

from langchain_openai import ChatOpenAI
from langgraph.graph import  add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from kenkenpa.builder import WorkFlowBuilder

# Toolノードは通常通り定義します。
@tool
def search(query: str):
    """Call to surf the web."""

    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."

# 別のToolも定義しておきましょう。
@tool
def search_un(query: str):
    """Call to surf the web."""
    return "I'm sorry, I don't understand."


# 今回はnodeと同様に、キーマッピングの仕組みを使って説明します。
tools = {
    "search_function":search,
    "search_unknown":search_un
    }

# Toolノードのジェネレーター関数を定義します。
def gen_tool_node(settings,flow_parameter):
    functions = settings['functions']

    tool_functions = []
    for function in functions:
        tool_functions.append(tools[function])

    tool_node = ToolNode(tool_functions)
    return tool_node

def gen_agent(settings,flow_parameter):
    functions = settings['functions']

    tool_functions = []
    for function in functions:
        tool_functions.append(tools[function])
    
    # LLMの設定
    model = ChatOpenAI(
        model="gpt-4o-mini"
    )

    model = model.bind_tools(tool_functions)

    # Define the function that calls the model
    def call_model(state):
        messages = state['messages']
        response = model.invoke(messages)
        # We return a list, because this will get added to the existing list
        return {"messages": [response]}
    
    return call_model

# should_continueの代わりに最終メッセージがtool_callsかを評価する関数を定義します。
def is_tool_message(state, config, **kwargs):
    """最後のメッセージがtool_callsかを評価します。"""
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return True
    return False

# サブグラフの設定を定義します。
# この定義はreact_agent_test.pyと全く同じものです。
react_agent_subgraph = {
    "workflow_type":"workflow",
    "flow_parameter":{
        "name":"React-Agent-Subgraph",
    },
    "state" : [ # TODO state項目を使用しない場合は設定しなくてもよい(optional)
        {
            "field_name": "messages",
            "type": "AnyMessage",
            "reducer":"add_messages"
        },
    ],
    "flows":[
        {
            "workflow_type":"node",
            "flow_parameter":{
                "name":"agent",
                "generator":"agent_node_generator",
            },
            "settings" : {
                "functions":[
                    "search_function",
                ],
            },
        },
        {
            "workflow_type":"node",
            "flow_parameter":{
                "name":"tools",
                "generator":"tool_node_generator",
            },
            "settings":{
                "functions":[
                    "search_function",
                ],
            },
        },
        {# ノーマルエッジ
            "workflow_type":"edge",
            "flow_parameter":{
                "start_key":"START",
                "end_key":"agent"
            },
        },
        {# 静的条件付きエッジ
            "workflow_type":"conditional_edge",
            "flow_parameter":{
                "start_key":"agent",
                "conditions":[
                    {
                        "expression": {
                            "eq": [{"type": "function", "name": "is_tool_message_function"}, True],
                        },
                        "result": "tools" 
                    },
                    {"default": "END"} 
                ]
            },
        },
        {# ノーマルノード
            "workflow_type":"edge",
            "flow_parameter":{
                "start_key":"tools",
                "end_key":"agent"
            },
        },
    ]
}

# 親グラフの設定を定義します。
graph_settings = {
    "workflow_type":"workflow",
    "flow_parameter":{
        "name":"React-Agent",
    },
    "state" : [ # TODO state項目を使用しない場合は設定しなくてもよい(optional)
        {
            "field_name": "messages",
            "type": "AnyMessage",
            "reducer":"add_messages"
        },
    ],
    "flows":[
        react_agent_subgraph, # flowsにreact_agent_subgraphを追加します。
        {# ノーマルエッジ
            "workflow_type":"edge",
            "flow_parameter":{
                "start_key":"START",
                "end_key":"React-Agent-Subgraph"
            },
        },
        {# ノーマルエッジ
            "workflow_type":"edge",
            "flow_parameter":{
                "start_key":"React-Agent-Subgraph",
                "end_key":"END"
            },
        },
    ]
}

class ConfigSchema(BaseModel): #pylint:disable=too-few-public-methods
    dummy : str = "dummy config"

def test_sample_subgraph():

    # graph_settingsからWorkFlowBuilderを生成します。
    workflow_builder = WorkFlowBuilder(graph_settings,ConfigSchema) # TODO Configは任意項目にする

    # 使用する型を登録します。
    workflow_builder.add_type("AnyMessage",AnyMessage)
    # 使用するreducerを登録します。
    workflow_builder.add_reducer("add_messages",add_messages)

    # workflow_builderにノードジェネレーターを登録しておきます。
    workflow_builder.add_node_generator("agent_node_generator",gen_agent)
    workflow_builder.add_node_generator("tool_node_generator",gen_tool_node)

    # 同様に、評価関数も登録します。
    workflow_builder.add_evaluete_function("is_tool_message_function", is_tool_message,)

    # getworkflowメソッドでコンパイル可能なStateGraphを取得できます。
    workflow = workflow_builder.getworkflow()

    # 以降はLangGraphの一般的な使用方法に従ってコードを記述します。
    memory = MemorySaver()
    app =  workflow.compile(checkpointer=memory,debug=False)
    print(f"\ngraph(xray=0)")
    app.get_graph(xray=0).print_ascii()

    print(f"\ngraph(xray=1)")
    app.get_graph(xray=1).print_ascii()

    final_state = app.invoke(
        {"messages": [HumanMessage(content="what is the weather in sf")]},
        config={"configurable": {"thread_id": 42}}
    )
    print(final_state["messages"][-1].content)

