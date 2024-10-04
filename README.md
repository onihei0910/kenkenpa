# kenkenpa

Generate a StateGraph of LangGraph that can be compiled from structured data.

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/kenkenpa)
![Version](https://img.shields.io/pypi/v/kenkenpa)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/onihei0910/kenkenpa/graph/badge.svg?token=Jk43Q4OFpU)](https://codecov.io/gh/onihei0910/kenkenpa)

## Note

This document is a translation of a text originally written in [Japanese](README.ja.md).

## Purpose of this Library
This library was created to handle multiple AI agents within a single application.
Examples of use:
 - When you want to build AI agents with different purposes for each room
 - When you want to provide a UI for end-users to build AI agents by pre-providing nodes as components
 - When you want to develop a project assistant that supports different development flows for each code repository
 - When you want to apply different approval flows for each categorized document

## Installation

``` sh
pip install kenkenpa
```

## Usage Example

I will explain how to use kenkenpa with the example of React-Agent.  
[https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)

In addition to React-Agent, several implementation patterns of LangGraph are posted on [kenkenpa_example](https://github.com/onihei0910/kenkenpa_example).

---

Define the Tool node as usual.

``` python
from langchain_core.tools import tool

@tool
def search(query: str):
    """Call to surf the web."""

    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."
```

Define the factory function for the Tool node.

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

Define the factory function for the agent node.

``` python
from langchain_openai import ChatOpenAI

def gen_agent(factory_parameter,flow_parameter):
    functions = factory_parameter['functions']

    tool_functions = []
    for function in functions:
        tool_functions.append(tools[function])

     # Setting up the LLM
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

Define a function to evaluate whether the last message is a tool call instead of should_continue.

``` python
def is_tool_message(state, config, **kwargs):
    """Evaluate whether the last message is a tool call."""
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return True
    return False
```

Create structured data representing a StateGraph.

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
                        # Transition to the tools node if the result of is_tool_message is True.
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

Generate a StateGraphBuilder from graph_settings.

``` python
from langchain_core.messages import HumanMessage
from langgraph.graph import  add_messages
from langgraph.checkpoint.memory import MemorySaver

from kenkenpa.builder import StateGraphBuilder

# Instantiate the StateGraphBuilder
stategraph_builder = StateGraphBuilder(graph_settings)

# Some preparations are needed to generate a compilable StateGraph.
# *1. Register the types to be used. (list is reserved, but it is written for explanation purposes.)
#stategraph_builder.add_type("list", list)

# *2. Register the reducers to be used.
stategraph_builder.add_reducer("add_messages",add_messages)

# *3. Register the Node Factories.
stategraph_builder.add_node_factory("agent_node_factory",gen_agent)
stategraph_builder.add_node_factory("tool_node_factory",gen_tool_node)

# *4. Register the evaluation functions as well.
stategraph_builder.add_evaluete_function("is_tool_message_function", is_tool_message,)

# You can obtain a compilable StateGraph with the gen_stategraph() method.
stategraph = stategraph_builder.gen_stategraph()

# From here, write the code following the general usage of LangGraph.
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

Execution Result

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

## Definition of graph settings

### Definition of `stategraph` (kenkenpa.models.stategraph.KStateGraph)

It represents a StateGraph.

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
- desc: Specifies the graph type. Fixed as stategraph.

#### `flow_parameter`

- type: Dict
- desc: Data referenced when generating the StateGraph.

##### `name`

- type: str
- desc: The name of the StateGraph. In the case of a subgraph, it will be the name displayed in  CompiledGraph. get_graph().

##### `state`

- type: List[Dict]
- desc: Describes the definition of custom states. Details are provided later.

#### `flows`

- type: List[Dict]
- desc: A list of definitions for StateGraph (SubGraph), node, and edge that make up the StateGraph.

### Definition of state (kenkenpa.models.stategraph.KState)

This is the state definition referenced by the StateGraph.
State is generated as  TypedDict.

``` python
"state" : [
    {
        "field_name": "messages",
        "type": "list",
        "reducer":"add_messages"
    },
]

# This definition corresponds to the following.
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import  add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

# Actual access
def is_tool_message(state, config, **kwargs):
    messages = state['messages']

```

#### `field_name`

- type: str
- desc: This is the field name.

#### `type`

- type: str
- his is a string representing the key for the field type.

The following types are pre-registered:
`int`,`float`,`complex`,`str`,`list`,`tuple`,`dict`,`set`,`frozenset`,`bool`

To use types other than the reserved ones, you need to register the type with the StateGraphBuilder.

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

# You can also pass it to the constructor.
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
- This is a string representing the key for the reducer.

To use a reducer, you need to register it with the StateGraphBuilder.[Full code](tests/example/conditional_branching_test.py)

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

# You can also pass it to the constructor.
reducer_map = {
    "operator_add": operator.add,
    "reducer_a_key": custom_reducer_a
}

stategraph_builder = StateGraphBuilder(
    graph_settings = graph_settings,
    reducers = reducer_map
    )

```

### Definition of node (kenkenpa.models.node.KNode)

This represents a single node.

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
- desc: Specifies the graph type. Fixed to `node`.

#### `flow_parameter`

- type: Dict
- desc: Data referenced when generating the StateGraph.

##### `name`

- type: str
- desc: The name of the node. This will be the name displayed in `CompiledGraph`.`get_graph()`.

##### `factory`

- type: str
- factory: Represents the factory function that generates the runnable functioning as a node.

#### `factory_parameter`

- type: Optional[Dict]
- desc: Parameters passed to the factory function.

The factory function is defined to accept `factory_parameter` and `flow_parameter`.

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

You can also define it as a class acceptable by LangGraph.

``` python
class Chatbot():
    def __init__(self,factory_parameter,flow_parameter):
        pass

    def __call__(self,state,config):
        return {"messages":[llm.invoke(state["messages"])]}

stategraph_builder = StateGraphBuilder(graph_settings)
stategraph_builder.add_node_factory("gen_chatbot_agent_key",Chatbot)

stategraph = stategraph_builder.gen_stategraph()

# You can also pass the factory function map to the constructor.
factory_map = {
    "gen_chatbot_agent_key": Chatbot,

}

stategraph_builder = StateGraphBuilder(
    graph_settings = graph_settings,
    node_factorys = factory_map
    )


```

### Definition of `edge` (kenkenpa.models.edge.KEdge)

Represents a single edge.

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
- desc: Specifies the graph type. Fixed to `edge`.

#### `flow_parameter`

- type: Dict
- desc: Data referenced when generating the StateGraph.

##### `start_key`

- type: Union[List[str],str]
- desc: Represents the starting point of the edge. Either `start_key` or `end_key` can be a list, but not both.

##### `end_key`

- type: Union[List[str],str]
- desc: Represents the endpoint of the edge. Either `start_key` or `end_key` can be a list, but not both.

### Definition of `configurable_conditional_edge` (kenkenpa.models.configurable_conditional_edge.KConfigurableConditionalEdge)

This is the definition of a conditional edge.

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
- desc: Specifies the graph type. Fixed to `configurable_conditional_edge`.

#### `flow_parameter`

- type: Dict
- desc: Data referenced when generating the StateGraph.

##### `start_key`

- type: str
- desc: The starting point of the edge.

##### `conditions`

- type: List[Union[KConditionExpression,KConditionDefault]]
- desc: Describes the conditional expressions to determine the next node. Details are provided below.

### Definition of `conditions` (kenkenpa.models.conditions.KConditions)

This is the definition to determine the next node based on the result of the evaluation expression. Let's explain in a bit more detail.

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

#### conditions List

You can define a list of evaluation expressions, each with an expression and a result.
If all expressions evaluate to false, the node specified in default will be transitioned to.

When routing based on the value of the state, it can be described as follows:

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

The conditions evaluate all expressions and specify all results that evaluate to True as the next nodes.
In the following example, both node_a and node_b are returned.

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
  Comparison and logical expressions can be used.

- ***Comparison Expressions***

  ``` python
  "operator": [operand,operand]
  ```

- Operators
  - `equals`,`eq`,`==`
  - `not_equals`,`neq`,`!=`
  - `greater_than`,`gt`,`>`
  - `greater_than_or_equals`,`gte`,`>=`
  - `less_than`,`lt`,`<`
  - `less_than_or_equals`,`lte`,`<=`

- Operands
  - state_value
    Refers to the value of the state.

    ``` python
    {"type":"state_value", "name":"state_key"}
    ```

  - config_value
    Refers to the value of the config.

    ``` python
    {"type":"config_value", "name":"test_config_key"}
    ```

  - function
    Calls a predefined evaluation function.

    ``` python
    {"type":"function","name":"test_function","args":{"args_key":"args_value"}}
    ```

  - Scalar values
    `int`,`float`,`complex`,`bool`,`str`,`bytes`,`None`

- Example 1
    Verifies if the result of calling the evaluation function mapped to "is_tool_message_function" is True.

    ``` python
    "expression": {
        "eq": [
            {"type": "function", "name": "is_tool_message_function"}, 
            True
        ],
    }
    ```

    To use an evaluation function, it must be mapped in the StateGraphBuilder.

    ``` python
    def is_tool_message(state, config, **kwargs):
        """Evaluates if the last message is a tool_call."""
        messages = state['messages']
        last_message = messages[-1]
        if last_message.tool_calls:
            return True
        return False

    # Generate StateGraphBuilder from graph_settings.
    stategraph_builder = StateGraphBuilder(graph_settings)
    # Register the evaluation function
    stategraph_builder.add_evaluete_function("is_tool_message_function", is_tool_message,)

    ```

- Example 2
    Verifies if the value of the state is "evaluate_value".

    ``` python
    "expression": {
        "eq": [
            {"type": "state_value", "name": "state_key"}, 
            "evaluate_value"
        ],
    }
    ```

- Example 3
    Refers to the value of the config.

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

- **Logical Expressions**

  ``` python
  "and": [evaluation expression or logical expression]
  "or" : [evaluation expression or logical expression]
  "not": evaluation expression or logical expression
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

  Logical expressions can be nested.

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

- **`result` and `default`**
The following values can be set.
  - state_value
    Refers to the value of the state. The value of the state must be a str (node name).

    ``` python
    {"type": "state_value", "name": "state_key"}
    ```

  - config_value
    Refers to the value of the config. The value of the config must be a str (node name).

    ``` python
    {"type": "config_value", "name": "config_key"}
    ```

  - function
    Calls a predefined evaluation function.
    The return value of the function must be a str (node name) or an instance of Send.

    ``` python
    {"type": "function", "name": "test_function", "args": {"args_key": "args_value"}}
    ```

  - Scalar values
    `str`

- Example  
The evaluation function can be used for purposes utilizing the Send API as follows. [Full code](tests/example/map_reduce_branches_for_parallel_execution_test.py)  

``` python
# Define continue_to_jokes so that it can be called as an evaluation function.
def continue_to_jokes(state: OverallState, config, **kwargs):
    return [Send("generate_joke", {"subject": s}) for s in state["subjects"]]

# Generate the StateGraphBuilder from graph_settings.
stategraph_builder = StateGraphBuilder(graph_settings)

# Similarly, the evaluation function is also registered.
stategraph_builder.add_evaluate_function("continue_to_jokes", continue_to_jokes)

graph_settings = {
    # (omitted)

    "flows": [
        {  # conditional edge generate_topics -> continue_to_jokes
            "graph_type": "configurable_conditional_edge",
            "flow_parameter": {
                "start_key": "generate_topics",
                "path_map": ["generate_joke"],  # Specify the path_map
                "conditions": [
                    # Define only the default in the conditions of configurable_conditional_edge,
                    # and call continue_to_jokes here.
                    {"default": {"type": "function", "name": "continue_to_jokes"}}
                ]
            },
        },
    ]
}
```
