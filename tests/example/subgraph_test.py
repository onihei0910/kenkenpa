"""
In this test, we will explain how to set up a subgraph.
We will define the react-agent, explained in react_agent_test.py, as a subgraph.
Some parts of the test code reuse the code listed at the following URL.
https://langchain-ai.github.io/langgraph/
"""
from langchain_core.messages import HumanMessage,AIMessage
from langchain_core.tools import tool

#from langchain_openai import ChatOpenAI
from langgraph.graph import  add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from kenkenpa.builder import StateGraphBuilder

# Define the Tool node as usual.
@tool
def search(query: str):
    """Call to surf the web."""

    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."

tools = {
    "search_function":search,
    }

# Define the factory function for the Tool node.
def gen_tool_node(factory_parameter,flow_parameter):
    functions = factory_parameter['functions']

    tool_functions = []
    for function in functions:
        tool_functions.append(tools[function])

    tool_node = ToolNode(tool_functions)
    return tool_node

# Define the factory function for the agent node.
def gen_agent(factory_parameter,flow_parameter):
    functions = factory_parameter['functions']

    tool_functions = []
    for function in functions:
        tool_functions.append(tools[function])

    #model = ChatOpenAI(
    #    model="gpt-4o-mini"
    #)

    #model = model.bind_tools(tool_functions)

    # Define the function that calls the model
    def call_model(state):
        messages = state['messages']
        #response = model.invoke(messages)
        # dummy
        response = AIMessage(content='This is dummy message')
        # We return a list, because this will get added to the existing list
        return {"messages": [response]}

    return call_model

# Define a function to evaluate whether the final message is a tool_call
# instead of should_continue.
def is_tool_message(state, config, **kwargs):
    """最後のメッセージがtool_callsかを評価します。"""
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return True
    return False

# Define the subgraph settings.
react_agent_subgraph = {
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
                "factory":"agent_node_factory",
            },
            "factory_parameter" : {
                "functions":[
                    "search_function",
                ],
            },
        },
        { # tools node
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
                        # Routing is described here.
                        # In this example, if the defined evaluation function returns True, it transitions to "tools",
                        # and if it returns False, it transitions to "END".
                        # The adjustment of edge drawing when calling the CompiledGraph.get_graph() method is done automatically.
                        # Please refer to the README for the structure of the evaluation expressions and the available operators.
                        "expression": {
                            "eq": [{"type": "function", "name": "is_tool_message_function"}, True],
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

# Define the parent graph settings.
graph_settings = {
    "graph_type":"stategraph",
    "flow_parameter":{
        "name":"Parent-Graph",
        "state" : [
            {
                "field_name": "messages",
                "type": "list",
                "reducer":"add_messages"
            },
        ],
    },
    "flows":[
        react_agent_subgraph, #  add react_agent_subgraph to flows.
        {# edge START -> React-Agent
            "graph_type":"edge",
            "flow_parameter":{
                "start_key":"START",
                "end_key":"React-Agent"
            },
        },
        {# edge React-Agent -> END
            "graph_type":"edge",
            "flow_parameter":{
                "start_key":"React-Agent",
                "end_key":"END"
            },
        },
    ]
}

def test_sample_subgraph():
    # Generate the StateGraphBuilder from graph_settings.
    stategraph_builder = StateGraphBuilder(graph_settings)

    # Register the reducer to be used in the StateGraphBuilder.
    stategraph_builder.add_reducer("add_messages",add_messages)

    # Register the node factory with the stategraph_builder.
    stategraph_builder.add_node_factory("agent_node_factory",gen_agent)
    stategraph_builder.add_node_factory("tool_node_factory",gen_tool_node)

    # Similarly, the evaluation function is also registered.
    stategraph_builder.add_evaluete_function("is_tool_message_function", is_tool_message,)

    # The gen_stategraph method generates a compilable StateGraph.
    stategraph = stategraph_builder.gen_stategraph()

    # From here on, we will write the code following the general usage of LangGraph.
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

