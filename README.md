# kenkenpa

Generate a StateGraph of LangGraph that can be compiled from structured data.

## Usage Example

React-Agentを例にkenkenpaの使用方法を説明します。
https://langchain-ai.github.io/langgraph/

``` python
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_core.messages import AnyMessage
from langchain_openai import ChatOpenAI

from langgraph.graph import  add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from kenkenpa.builder import StateGraphBuilder
```

Toolノードは通常通り定義します。

``` python
@tool
def search(query: str):
    """Call to surf the web."""

    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."
```

Toolノードのファクトリー関数を定義します。

``` python
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
```

agentノードのファクトリー関数を定義します。

``` python
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
```

should_continueの代わりに最終メッセージがtool_callsかを評価する関数を定義します。

``` python
def is_tool_message(state, config, **kwargs):
    """最後のメッセージがtool_callsかを評価します。"""
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return True
    return False
```

StateGraphの構造化データを作成します。

``` python
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
            "graph_type":"static_conditional_edge",
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
```

graph_settingsからStateGraphBuilderを生成します。

``` python
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
stategraph_builder.add_evaluete_function("is_tool_message_function", s_tool_message,)

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
```

実行結果

``` shell
        +-----------+         
        | __start__ |         
        +-----------+         
              *               
              *               
              *               
          +-------+           
          | agent |           
          +-------+           
         .         .          
       ..           ..        
      .               .       
+-------+         +---------+ 
| tools |         | __end__ | 
+-------+         +---------+ 

The current weather in San Francisco is 60 degrees and foggy.
```

React-Agent以外の使用例のいくつかをテストとして記述してあります。

## graph settings定義

### `stategraph`の定義(kenkenpa.models.stategraph.KStateGraph)

1つのStateGraphを表します。
  
``` python
{
    "graph_type":"stategraph",
    "flow_parameter":{
        "name":"GraphName",
        "state" : [
            {
                "field_name": "messages",
                "type": "list",
                "reducer":"add_messages"
            },
        ],
    },
    "flows":[
        #stategraph | node | edge | static_conditional_edge | static_conditional_entory_point
    ]
}

```

#### `graph_type`

- type: str
- desc: graphタイプを指定します。`stategraph`固定です。

#### `flow_parameter`

- type: Dict
- desc: StateGraph生成時に参照されるデータです。

##### `name`

- type: str
- desc: StateGraphの名前。サブグラフの場合、`CompiledGraph`.`get_graph()`で表示される名称になります。

##### `state`

- type: List[Dict]
- desc: カスタムステートの定義を記述します。詳細は後述。  

#### `flows`

- type: List[Dict]
- desc: StateGraphを構成するStateGraph(SubGraph),node,edge定義のリスト。

### `state`の定義(kenkenpa.models.stategraph.KState)

StateGraphが参照するState定義です。
Stateは`TypedDict`として生成されます。

``` python
"state" : [
    {
        "field_name": "messages",
        "type": "list",
        "reducer":"add_messages"
    },
]
```

この定義は以下に相当します。

``` python
from typing_extensions import TypedDict
from langgraph.graph import  add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

# 実際のアクセス
def is_tool_message(state, config, **kwargs):
    messages = state['messages']

```

#### `field_name`

- type: str
- desc: フィールドネームです。

#### `type`

- type: str
- フィールドの型を表すキーの文字列です。

以下の型は事前に登録されています。
`int`,`float`,`complex`,`str`,`list`,`tuple`,`dict`,`set`,`frozenset`,`bool`

予約済みの型以外を使用するにはStateGraphBuilderに型を登録しておく必要があります。

``` python
#...
#"state" : [
#    {
#        "field_name": "somestate_field",
#        "type": "SomeType_Key",
#    }
#]
#...

class SomeType(TypedDict):
    column: str

stategraph_builder = StateGraphBuilder(graph_settings)
stategraph_builder.add_type("SomeType_Key",SomeType)

# コンストラクタに渡すこともできます。
type_map = {
    "SomeType_Key": SomeType
}

stategraph_builder = StateGraphBuilder(
    graph_settings = graph_settings,
    types = type_map
    )

```

#### `reducer`

- type: str
- reducerを表すキーの文字列です。

reducerを使用するにはStateGraphBuilderにreducerを登録しておく必要があります。

``` python
import operator

#...
#"state" : [
#    {
#        "field_name": "messages",
#        "type": "list",
#        "reducer":"operator_add"
#    },
#    {
#        "field_name": "custom_reduser",
#        "type": "list",
#        "reducer":"reducer_a_key"
#    },
#]
#...

def custom_reducer_a(left,right):
    if left is None:
        left = []
    if not right:
        return []
    return left + right

stategraph_builder = StateGraphBuilder(graph_settings)
stategraph_builder.add_reducer("operator_add",operator.add)
stategraph_builder.add_reducer("reducer_a_key",custom_reducer_a)

# コンストラクタに渡すこともできます。
reducer_map = {
    "operator_add": operator.add,
    "reducer_a_key": custom_reducer_a
}

stategraph_builder = StateGraphBuilder(
    graph_settings = graph_settings,
    reducers = reducer_map
    )

```

### `node`の定義(kenkenpa.models.node.KNode)

1つのnodeを表します。

``` python
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
}

```

#### `graph_type`

- type: str
- desc: graphタイプを指定します。`node`固定です。

#### `flow_parameter`

- type: Dict
- desc: StateGraph生成時に参照されるデータです。

##### `name`

- type: str
- desc: nodeの名前。`CompiledGraph`.`get_graph()`で表示される名称になります。

##### `factory`

- type: str
- factory: nodeとして機能するrunnableを生成するファクトリー関数を表します。

#### `factory_parameter`

- type: Optional[Dict]
- desc: ファクトリー関数に渡されるパラメータです。
  
ファクトリ関数は`factory_parameter`と`flow_parameter`を受け取る様に定義します。

``` python
#{
#    "graph_type":"node",
#    "flow_parameter":{
#        "name":"chatbot",
#        "factory":"gen_chatbot_agent_key",
#    },
#    "factory_parameter" : {
#        "functions":[
#            "search_function",
#        ],
#    },
#}
# node
def chatbot(state,config):
    return {"messages":[llm.invoke(state["messages"])]}

# factory
def gen_chatbot_agent(factory_parameter,flow_parameter):
    return chatbot

stategraph_builder = StateGraphBuilder(graph_settings)
stategraph_builder.add_node_factory("gen_chatbot_agent_key",gen_chatbot_agent)

stategraph = stategraph_builder.gen_stategraph()
```

LangGraphが受け入れ可能なClassとしての定義もできます。

``` python
class Chatbot():
    def __init__(self,factory_parameter,flow_parameter):
        pass

    def __call__(self,state,config):
        return {"messages":[llm.invoke(state["messages"])]}

stategraph_builder = StateGraphBuilder(graph_settings)
stategraph_builder.add_node_factory("gen_chatbot_agent_key",Chatbot)

stategraph = stategraph_builder.gen_stategraph()

# ファクトリー関数のマップはコンストラクタに渡すこともできます。
factory_map = {
    "gen_chatbot_agent_key": Chatbot,

}

stategraph_builder = StateGraphBuilder(
    graph_settings = graph_settings,
    node_factorys = factory_map
    )


```

### `edge`の定義(kenkenpa.models.edge.KEdge)

1つのedgeを表します。

``` python
{
    "graph_type":"edge",
    "flow_parameter":{
        "start_key":"START",
        "end_key":"test_node_a"
    },
}
```

#### `graph_type`

- type: str
- desc: graphタイプを指定します。`edge`固定です。

#### `flow_parameter`

- type: Dict
- desc: StateGraph生成時に参照されるデータです。

##### `start_key`

- type: Union[List[str],str]
- desc: edgeの始点を表します。`start_key`と`end_key`のいずれか一方のみをlistにできます。

##### `end_key`

- type: Union[List[str],str]
- desc: edgeの終点を表します。`start_key`と`end_key`のいずれか一方のみをlistにできます。

### `static_conditional_edge`の定義(kenkenpa.models.static_conditional_edge.KStaticConditionalEdge)

conditional_edgeの定義です。

``` python
{
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
    }
}

```

#### `graph_type`

- type: str
- desc: graphタイプを指定します。`static_conditional_edge`固定です。

#### `flow_parameter`

- type: Dict
- desc: StateGraph生成時に参照されるデータです。

##### `start_key`

- type: str
- desc: edgeの始点です。

##### `conditions`

- type: List[Union[KConditionExpression,KConditionDefault]]
- desc: 次のnodeを決定するための条件式を記述します。詳細は後述。

### `conditions`の定義(kenkenpa.models.conditions.KConditions)

``` python
"conditions":[
    {
        "expression": {
            "eq": [{"type": "function", "name": "is_tool_message_function"}, True],
        },
        "result": "tools"
    },
    {"default": "END"} 
]
```