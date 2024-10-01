# kenkenpa

構造化データからコンパイル可能なLangGraphのStateGraphを生成します。

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/kenkenpa)
![Version](https://img.shields.io/pypi/v/kenkenpa)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/onihei0910/kenkenpa/graph/badge.svg?token=Jk43Q4OFpU)](https://codecov.io/gh/onihei0910/kenkenpa)

## インストール

``` sh
pip install kenkenpa
```

## 使用例

React-Agentを例にkenkenpaの使用方法を説明します。  
[https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)

React-Agentのほか、LangGraphの実装パターンのいくつかを[test](https://github.com/onihei0910/kenkenpa/tree/main/tests/example)として記述してあります。

Toolノードは通常通り定義します。

``` python
from langchain_core.tools import tool

@tool
def search(query: str):
    """Call to surf the web."""

    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."
```

Toolノードのファクトリー関数を定義します。

``` python
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
```

agentノードのファクトリー関数を定義します。

``` python
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

StateGraphを表す構造化データを作成します。

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
```

graph_settingsからStateGraphBuilderを生成します。

``` python
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
        #stategraph | node | edge | configurable_conditional_edge | configurable_conditional_entory_point
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

# この定義は以下に相当します。
from typing import Annotated
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

予約済みの型以外はStateGraphBuilderに登録しておく必要があります。

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

reducerを使用するにはStateGraphBuilderに登録しておく必要があります。[コード全文](tests/example/conditional_branching_test.py)

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

### `configurable_conditional_edge`の定義(kenkenpa.models.configurable_conditional_edge.KConfigurableConditionalEdge)

conditional_edgeの定義です。

``` python
{
    "graph_type":"configurable_conditional_edge",
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
- desc: graphタイプを指定します。`configurable_conditional_edge`固定です。

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

評価式の結果に応じて次のnodeを決定させるための定義です。少し詳しく説明します。

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

#### conditionsリスト

1つのexpressionとresultを持つ評価式をリストとして定義できます。
いずれのexpressionも偽となった場合はdefaultに指定されたnodeに遷移します。

stateの値に応じてルーティングする場合は以下のような記述になります。

``` python
"conditions":[
    {
        "expression": {
            "eq": [{"type": "state_value", "name": "next_node"}, "node_a"],
        },
        "result": "node_a"
    },
    {
        "expression": {
            "eq": [{"type": "state_value", "name": "next_node"}, "node_b"],
        },
        "result": "node_b"
    },
    {
        "expression": {
            "eq": [{"type": "state_value", "name": "next_node"}, "node_c"],
        },
        "result": "node_c"
    },
    {"default": "END"} 
]
```

conditionsは、全ての評価式を評価し、結果がTrueになったすべてのresultを次のnodeに指定します。  
以下の例では、node_aとnode_bを返します。

``` python
"conditions":[
    {
        "expression": {
            "eq": [True, True],
        },
        "result": "node_a"
    },
    {
        "expression": {
            "eq": [True, True],
        },
        "result": "node_b"
    },
    {"default": "END"} 
]
```

- **expression**
  比較式と論理式が使えます。  

- **比較式**

  ``` python
  "operator": [operand,operand]
  ```

- オペレータ
  - `equals`,`eq`,`==`
  - `not_equals`,`neq`,`!=`
  - `greater_than`,`gt`,`>`
  - `greater_than_or_equals`,`gte`,`>=`
  - `less_than`,`lt`,`<`
  - `less_than_or_equals`,`lte`,`<=`

- オペランド
  - state_value
    stateの値を参照します。

    ``` python
    {"type":"state_value", "name":"state_key"}
    ```

  - config_value
    configの値を参照します。

    ``` python
    {"type":"config_value", "name":"config_key"}
    ```

  - function
    定義済みの評価関数を呼び出します。

    ``` python
    {"type":"function","name":"test_function","args":{"args_key":"args_value"}}
    ```

  - スカラー値
    `int`,`float`,`complex`,`bool`,`str`,`bytes`,`None`

- 使用例1

    "is_tool_message_function"にマッピングした評価関数を呼び出し結果がTrueかを検証します。

    ``` python
    "expression": {
        "eq": [
            {"type": "function", "name": "is_tool_message_function"}, 
            True
        ],
    }
    ```

    評価関数を使用するにはStateGraphBuilderにマッピングしておく必要があります。

    ``` python
    def is_tool_message(state, config, **kwargs):
        """最後のメッセージがtool_callsかを評価します。"""
        messages = state['messages']
        last_message = messages[-1]
        if last_message.tool_calls:
            return True
        return False

    # graph_settingsからStateGraphBuilderを生成します。
    stategraph_builder = StateGraphBuilder(graph_settings)
    # 評価関数の登録
    stategraph_builder.add_evaluete_function("is_tool_message_function", is_tool_message,)

    ```

- 使用例2
    stateの値を参照して"evaluate_value"かを検証します。

    ``` python
    "expression": {
        "eq": [
            {"type": "state_value", "name": "state_key"}, 
            "evaluate_value"
        ],
    }
    ```

- 使用例3
    configの値を参照します

    ``` python
    config = {
        "configurable": {
            "thread_id":42,
            "user_id": "123",
            "tool_permission": True
        }
    }

    "expression": {
        "eq": [
            {"type": "config_value", "name": "tool_permission"}, 
            True
        ],
    }
    ```

- **論理式**

  ``` python
  "and": [評価式 or 論理式]
  "or" : [評価式 or 論理式]
  "not": 評価式 or 論理式
  ```

  ``` python
  "expression": {
      "and": [
          {"eq": [{"type": "function", "name": "is_tool_message_function"}, True]},
          {"eq": [{"type": "state_value", "name": "tool_call"}, True]},
      ]
  }
  ```

  ``` python
  "expression": {
      "or": [
          {"eq": [{"type": "function", "name": "is_tool_message_function"}, True]},
          {"eq": [{"type": "state_value", "name": "tool_call"}, True]},
      ]
  }
  ```

  ``` python
  "expression": {
      "not":{
          "eq": [{"type": "function", "name": "is_tool_message_function"}, True]
      }
  }
  ```

  論理式は入れ子にできます。

  ``` python
  "expression": {
      "and":[
          {
              "or":[
                  {
                      "and":[
                          {"eq": ["10", "10"]},
                          {"eq": [True, True]},
                          ]
                  },
                  {"eq": ["10", "10"]}
                  ]
          },
          {"eq": ["10", "10"]},
      ],
  }
  ```

- **`result`と`default`**
以下の値を設定できます。

  - state_value
    stateの値を参照します。stateの値はstr(ノード名)である必要があります。

    ``` python
    {"type":"state_value", "name":"state_key"}
    ```

  - config_value
    configの値を参照します。configの値はstr(ノード名)である必要があります。

    ``` python
    {"type":"config_value", "name":"config_key"}
    ```

  - function
    定義済みの評価関数を呼び出します。
    関数の戻り値はstr(ノード名)かSendのインスタンスである必要があります。

    ``` python
    {"type":"function","name":"test_function","args":{"args_key":"args_value"}}
    ```

  - スカラー値
    `str`

- 使用例  
評価関数は以下のように、Send APIを利用する用途で使えます。[コード全文](tests/example/map_reduce_branches_for_parallel_execution_test.py)

``` python
# continue_to_jokesは評価関数として呼び出し可能なように定義します。
def continue_to_jokes(state:OverallState, config, **kwargs):
    return [Send("generate_joke",{"subject":s}) for s in state["subjects"]]

# Generate the StateGraphBuilder from graph_settings.
stategraph_builder = StateGraphBuilder(graph_settings)

# Similarly, the evaluation function is also registered.
stategraph_builder.add_evaluete_function("continue_to_jokes", continue_to_jokes)

graph_settings = {
    # (省略)

    "flows":[
        {　# coditional edge generate_topics -> continue_to_jokes
            "graph_type":"configurable_conditional_edge",
            "flow_parameter":{
                "start_key":"generate_topics",
                "path_map":["generate_joke"], # path_mapを指定します
                "conditions":[
                    # configurable_conditional_edgeのconditionsにdefaultのみを定義し、
                    # ここでcontinue_to_jokesを呼び出すようにします。
                    {"default": {"type": "function", "name": "continue_to_jokes"}} 
                ]
            },
        },
    ]
}

```
