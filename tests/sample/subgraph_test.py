"""
このテストでは、サブグラフの設定方法を説明します。
react_agent_test.pyで説明したreact-agentをサブグラフとして設定します。
"""
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_core.messages import AnyMessage

from langchain_openai import ChatOpenAI
from langgraph.graph import  add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from kenkenpa.builder import StateGraphBuilder

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
def gen_tool_node(factory_parameter,flow_parameter):
    functions = factory_parameter['functions']

    tool_functions = []
    for function in functions:
        tool_functions.append(tools[function])

    tool_node = ToolNode(tool_functions)
    return tool_node

def gen_agent(factory_parameter,flow_parameter):
    functions = factory_parameter['functions']

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
    "graph_type":"stategraph",
    "flow_parameter":{
        "name":"React-Agent-Subgraph",
        "state" : [
            {
                "field_name": "messages",
                "type": "list",
                "reducer":"add_messages"
            },
        ],
    },
    "flows":[
        {
            "graph_type":"node",
            "flow_parameter":{
                "name":"agent",
                "factory":"agent_node_factory",
            },
            "factory_parameter" : {
                "functions":[
                    "search_function",
                ],
            },
        },
        {
            "graph_type":"node",
            "flow_parameter":{
                "name":"tools",
                "factory":"tool_node_factory",
            },
            "factory_parameter":{
                "functions":[
                    "search_function",
                ],
            },
        },
        {# ノーマルエッジ
            "graph_type":"edge",
            "flow_parameter":{
                "start_key":"START",
                "end_key":"agent"
            },
        },
        {# 静的条件付きエッジ
            "graph_type":"static_conditional_edge",
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
            "graph_type":"edge",
            "flow_parameter":{
                "start_key":"tools",
                "end_key":"agent"
            },
        },
    ]
}

# 親グラフの設定を定義します。
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
        react_agent_subgraph, # flowsにreact_agent_subgraphを追加します。
        {# ノーマルエッジ
            "graph_type":"edge",
            "flow_parameter":{
                "start_key":"START",
                "end_key":"React-Agent-Subgraph"
            },
        },
        {# ノーマルエッジ
            "graph_type":"edge",
            "flow_parameter":{
                "start_key":"React-Agent-Subgraph",
                "end_key":"END"
            },
        },
    ]
}

def test_sample_subgraph():

    # graph_settingsからStateGraphBuilderを生成します。
    stategraph_builder = StateGraphBuilder(graph_settings)

    # 使用する型を登録します。
    stategraph_builder.add_type("AnyMessage",AnyMessage)
    # 使用するreducerを登録します。
    stategraph_builder.add_reducer("add_messages",add_messages)

    # stategraph_builderにノードジェネレーターを登録しておきます。
    stategraph_builder.add_node_factory("agent_node_factory",gen_agent)
    stategraph_builder.add_node_factory("tool_node_factory",gen_tool_node)

    # 同様に、評価関数も登録します。
    stategraph_builder.add_evaluete_function("is_tool_message_function", is_tool_message,)

    # gen_stategraphメソッドでコンパイル可能なStateGraphを取得できます。
    stategraph = stategraph_builder.gen_stategraph()

    # 以降はLangGraphの一般的な使用方法に従ってコードを記述します。
    memory = MemorySaver()
    app =  stategraph.compile(checkpointer=memory,debug=False)
    print(f"\ngraph(xray=0)")
    app.get_graph(xray=0).print_ascii()

    print(f"\ngraph(xray=1)")
    app.get_graph(xray=1).print_ascii()

    final_state = app.invoke(
        {"messages": [HumanMessage(content="what is the weather in sf")]},
        config={"configurable": {"thread_id": 42}}
    )
    print(final_state["messages"][-1].content)

