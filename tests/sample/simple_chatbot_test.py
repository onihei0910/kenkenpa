"""
このテストは、LangGraphのsimple chatbotを例にkenkenpaの使用方法を説明します。
https://langchain-ai.github.io/langgraph/tutorials/introduction/
"""
from langchain_openai import ChatOpenAI

from langgraph.graph import  add_messages
from langgraph.checkpoint.memory import MemorySaver

from kenkenpa.builder import StateGraphBuilder

# LLMの設定
llm = ChatOpenAI(
    model="gpt-4o-mini"
)

# Nodeとなるchatbot関数を定義します。ここはQuickStart通りです。
def chatbot(state,config):
    return {"messages":[llm.invoke(state["messages"])]}

# chatbotとは別に、定義したchatbotを返すファクトリー関数を定義します。
def gen_chatbot_agent(factory_parameter,flow_parameter):
    """chatbot node factory"""
    return chatbot

class Chatbot():
    def __init__(self,factory_parameter,flow_parameter):
        pass

    def __call__(self,state,config):
        return {"messages":[llm.invoke(state["messages"])]}


# コンパイル可能なStateGraphの設定を辞書形式で記述します。
graph_settings = {
    "graph_type":"stategraph",
    "flow_parameter":{
        "name":"React-Agent",
        "state" : [ # TODO state項目を使用しない場合は設定しなくてもよい(optional)
            {
                "field_name": "messages",
                "type": "list",
                "reducer":"add_messages"
            },
        ],
    },
    "flows": [
        { # node chatbotの定義です。
            "graph_type":"node",
            "flow_parameter": {
                "name":"chatbot_agent",
                # factoryに定義したファクトリー関数gen_chatbot_agentとマッピングする文字列を指定します。
                # マッピングはコード実行時に指定します。
                "factory":"chatbot_factory", 
            },
        },
        { # normal_edge START-> chatbot_agent
            "graph_type":"edge",
            "flow_parameter":{
                "start_key":"START",
                "end_key":"chatbot_agent"
            },
        },
        { # normal_edge chatbot_agent-> END
            "graph_type":"edge",
            "flow_parameter": {
                "start_key":"chatbot_agent",
                "end_key":"END"
            },
        },
    ]
}

def test_sample_simple_chatbot():
    # graph_settingsからStateGraphBuilderを生成します。
    stategraph_builder = StateGraphBuilder(graph_settings)

    # 使用する型を登録します。
    #stategraph_builder.add_type("AnyMessage",AnyMessage)
    # 使用するreducerを登録します。
    stategraph_builder.add_reducer("add_messages",add_messages)

    # stategraph_builderにノードファクトリーを登録しておきます。
    # ここでは、gen_chatbot_agent関数をchatbot_factoryにマッピングしています。
    # graph_settingsに記載したキー値と一致しているか確認してください。
    #stategraph_builder.add_node_factory("chatbot_factory",gen_chatbot_agent)
    stategraph_builder.add_node_factory("chatbot_factory",Chatbot)

    # gen_stategraphメソッドでコンパイル可能なStateGraphを取得できます。
    stategraph = stategraph_builder.gen_stategraph()

    # 以降はLangGraphの一般的な使用方法に従ってコードを記述します。
    memory = MemorySaver()

    app =  stategraph.compile(checkpointer=memory,debug=False)

    print(f"\ngraph")
    app.get_graph(xray=10).print_ascii()

    config = {"configurable": {"thread_id": "1"}}

    user_input = "Hi there! My name is Will."

    number_of_events = 0
    events = app.stream(
        {"messages": [("user", user_input)]}, config, stream_mode="values"
    )
    for event in events:
        number_of_events = number_of_events + 1
        event["messages"][-1].pretty_print()

    assert number_of_events == 2
