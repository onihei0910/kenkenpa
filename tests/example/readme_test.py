import pytest

def test_readmeja_example():
    ## 使用例

    # React-Agentを例にkenkenpaの使用方法を説明します。  
    # [https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)

    # React-Agentのほか、LangGraphの実装パターンのいくつかをtestとして記述してあります。

    # Toolノードは通常通り定義します。

    # ``` python
    from langchain_core.tools import tool

    @tool
    def search(query: str):
        """Call to surf the web."""

        if "sf" in query.lower() or "san francisco" in query.lower():
            return "It's 60 degrees and foggy."
        return "It's 90 degrees and sunny."
    # ```

    # Toolノードのファクトリー関数を定義します。

    # ``` python
    from langgraph.prebuilt import ToolNode

    tools = {
        "search_function":search,
        }

    def gen_tool_node(factory_parameter,flow_parameter):
        functions = factory_parameter['functions']

        tool_functions = []
        for function in functions:
            tool_functions.append(tools[function])

        tool_node = ToolNode(tool_functions)
        return tool_node
    # ```

    # agentノードのファクトリー関数を定義します。

    # ``` python
    from langchain_openai import ChatOpenAI

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
    # ```

    # should_continueの代わりに最終メッセージがtool_callsかを評価する関数を定義します。

    # ``` python
    def is_tool_message(state, config, **kwargs):
        """最後のメッセージがtool_callsかを評価します。"""
        messages = state['messages']
        last_message = messages[-1]
        if last_message.tool_calls:
            return True
        return False
    # ```

    # StateGraphを表す構造化データを作成します。

    # ``` python
    graph_settings = {
        "graph_type":"stategraph",
        "flow_parameter":{
            "name":"React-Agent",
            "state" : [
                {
                    "field_name": "messages", # state name
                    "type": "list", # type(*1)
                    "reducer":"add_messages" # reducer(*2)
                },
            ],
        },
        "flows":[
            { # agent node(*3)
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
            { # tools node(*3)
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
                            # is_tool_messageの結果がTrueの時にtools nodeに遷移します。
                            "expression": {
                                "eq": [{"type": "function", "name": "is_tool_message_function"}, True], # *4
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
    # ```

    # graph_settingsからStateGraphBuilderを生成します。

    # ``` python
    from langchain_core.messages import HumanMessage
    from langgraph.graph import  add_messages
    from langgraph.checkpoint.memory import MemorySaver
    
    from kenkenpa.builder import StateGraphBuilder

    # StateGraphBuilderのインスタンス化
    stategraph_builder = StateGraphBuilder(graph_settings)

    # コンパイル可能なStateGraphを生成するにはいくつかの準備が必要です。
    # *1. 使用する型を登録します。(listは予約されていますが、説明のために記述しています。)
    #stategraph_builder.add_type("list",list)

    # *2. 使用するreducerを登録します。
    stategraph_builder.add_reducer("add_messages",add_messages)

    # *3. Node Factoryを登録します。
    stategraph_builder.add_node_factory("agent_node_factory",gen_agent)
    stategraph_builder.add_node_factory("tool_node_factory",gen_tool_node)

    # *4. 評価関数も登録します。
    stategraph_builder.add_evaluete_function("is_tool_message_function", is_tool_message,)

    # gen_stategraph()メソッドでコンパイル可能なStateGraphを取得できます。
    stategraph = stategraph_builder.gen_stategraph()

    # 以降はLangGraphの一般的な使用方法に従ってコードを記述します。
    memory = MemorySaver()
    app =  stategraph.compile(checkpointer=memory,debug=False)

    print(f"\ngraph")
    app.get_graph().print_ascii()
    final_state = app.invoke(
        {"messages": [HumanMessage(content="what is the weather in sf")]},
        config={"configurable": {"thread_id": 42}}
    )
    print(final_state["messages"][-1].content)
    # ```