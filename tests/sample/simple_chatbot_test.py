"""
このテストは、LangGraphのsimple chatbotを例にdict_to_lg_workflowの使用方法を説明します。
https://langchain-ai.github.io/langgraph/tutorials/introduction/
"""
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.messages import AnyMessage
from langchain_openai import ChatOpenAI

from langgraph.graph import  add_messages
from langgraph.checkpoint.memory import MemorySaver

from dict_to_lg_workflow.builder import WorkFlowBuilder

class ConfigSchema(BaseModel): #pylint:disable=too-few-public-methods
    dummy : str = "dummy config"

# LLMの設定
llm = ChatOpenAI(
    model="gpt-4o-mini"
)

# Nodeとなるchatbot関数を定義します。ここはQuickStart通りです。
def chatbot(state,config):
    return {"messages":[llm.invoke(state["messages"])]}

# chatbotとは別に、定義したchatbotを返すジェネレーター関数を定義します。
def gen_chatbot_agent(metadata,settings):
    """chatbot node generator"""
    return chatbot

# コンパイル可能なStateGraphの設定を辞書形式で記述します。
graph_settings = {
    "metadata":{
        "workflow_type":"workflow",
        "flow_parameter":{
            "name":"React-Agent",
        }
    },
    "state" : [ # TODO state項目を使用しない場合は設定しなくてもよい(optional)
        {
            "field_name": "messages",
            "type": "AnyMessage",
            "reducer":"add_messages"
        },
    ],
    "flows": [
        { # node chatbotの定義です。
            "metadata" : {
                "workflow_type":"node",
                "flow_parameter": {
                    "name":"chatbot_agent",
                    # generatorに定義したジェネレーター関数gen_chatbot_agentとマッピングする文字列を指定します。
                    # マッピングはコード実行時に指定します。
                    "generator":"chatbot_generator", 
                }
            },
            "settings" : {}, # TODO settingsが無い場合は設定しなくてもよい。(optional)
        },
        { # normal_edge START-> chatbot_agent
            "metadata" :{
                "workflow_type":"edge",
                "flow_parameter":{
                    "start_key":"START",
                    "end_key":"chatbot_agent"
                }
            },
        },
        { # normal_edge chatbot_agent-> END
            "metadata" :{
                "workflow_type":"edge",
                "flow_parameter": {
                    "start_key":"chatbot_agent",
                    "end_key":"END"
                }
            },
        },
    ]
}

def test_sample_simple_chatbot():
    # graph_settingsからWorkFlowBuilderを生成します。
    workflow_builder = WorkFlowBuilder(graph_settings,ConfigSchema) # TODO Configは任意項目にする

    # 使用する型を登録します。
    workflow_builder.add_type("AnyMessage",AnyMessage)
    # 使用するreducerを登録します。
    workflow_builder.add_reducer("add_messages",add_messages)

    # workflow_builderにノードジェネレーターを登録しておきます。
    # ここでは、gen_chatbot_agent関数をchatbot_generatorにマッピングしています。
    # graph_settingsに記載したキー値と一致しているか確認してください。
    workflow_builder.add_node_generator("chatbot_generator",gen_chatbot_agent)

    # getworkflowメソッドでコンパイル可能なStateGraphを取得できます。
    workflow = workflow_builder.getworkflow()

    # 以降はLangGraphの一般的な使用方法に従ってコードを記述します。
    memory = MemorySaver()

    app =  workflow.compile(checkpointer=memory,debug=False)

    print("graph")
    app.get_graph(xray=10).print_ascii()

    config = {"configurable": {"thread_id": "1"}}

    user_input = "Hi there! My name is Will."

    number_of_events = 0
    events = app.stream(
        {"messages": [("user", user_input)]}, config, stream_mode="values"
    )
    for event in events:
        number_of_events = number_of_events + 1
        #event["messages"][-1].pretty_print()
        print(event["messages"][-1])

    assert number_of_events == 2
