"""
https://langchain-ai.github.io/langgraph/how-tos/map-reduce/
poetry run pytest tests/sample/map_reduce_branches_for_parallel_execution_test.py --capture=no
"""
import operator
import pytest
from typing import Annotated, TypedDict

from langchain_openai import ChatOpenAI

from langgraph.types import Send
from langgraph.graph import END, StateGraph, START

from pydantic import BaseModel, Field

# Model and prompts
# Define model and prompts we will use

# {topic}に関連する2から5の例をカンマで区切って生成してください。
subjects_prompt = """Generate a comma separated list of between 2 and 5 examples related to: {topic}."""

#{subject}に関するジョークを生成してください
joke_prompt = """Generate a joke about {subject}"""

# 以下は{topic}に関するたくさんのジョークです。最高のものを選んでください！最高のもののIDを返してください。{jokes}
best_joke_prompt = """Below are a bunch of jokes about {topic}. Select the best one! Return the ID of the best one.

{jokes}"""

class Subjects(BaseModel):
    subjects: list[str]

class Joke(BaseModel):
    joke: str

class BestJoke(BaseModel):
    #最高のジョークのインデックス。0から始まる
    id: int = Field(description="Index of the best joke. starting with 0",ge=0)

model = ChatOpenAI(model="gpt-4o-mini")

# This will be the overall state of the main graph.
# It will contain a topic (which we expect the user to provide)
# and then will generate a list of subjects, and then a joke for
# each subject
# これはメイングラフの全体的な状態になります。
# これにはトピック（ユーザーが提供することを期待しています）が含まれ、
# その後、各サブジェクトに対してリストを生成し、ジョークを生成します。
class OverallState(TypedDict):
    topic: str
    subjects: list
    # Notice here we use the operator.add
    # This is because we want combine all the jokes we generate
    # from individual nodes back into one list - this is essentially
    # the "reduce" part
    # ここで operator.add を使用していることに注意してください
    # これは、個々のノードから生成されたすべてのジョークを
    # 1つのリストにまとめたいからです - これは本質的に
    # 「reduce」部分です
    jokes: Annotated[list, operator.add]
    best_selected_joke: str

# This will be the state of the node that we will "map" all
# subjects to in order to generate a joke
# これは、ジョークを生成するためにすべての主題を「マッピング」するノードの状態です
class JokeState(TypedDict):
    subject: str

# This is the function we will use to generate the subjects of the jokes
# これはジョークの題材を生成するために使用する関数です
def generate_topics(state: OverallState):
    prompt = subjects_prompt.format(topic=state["topic"])
    response = model.with_structured_output(Subjects).invoke(prompt)
    return {"subjects": response.subjects}

# Here we generate a joke, given a subject
# ここでは、主題を与えられたジョークを生成します。
def generate_joke(state: JokeState):
    prompt = joke_prompt.format(subject=state["subject"])
    response = model.with_structured_output(Joke).invoke(prompt)
    return {"jokes": [response.joke]}

# Here we define the logic to map out over the generated subjects
# We will use this an edge in the graph
#ここでは、生成された主題に対してマッピングするロジックを定義します。
#これをグラフのエッジとして使用します。
def continue_to_jokes(state:OverallState):
    # We will return a list of `Send` objects
    # Each `Send` object consists of the name of a node in the graph
    # as well as the state to send to that node
    # Sendオブジェクトのリストを返します
    # 各`Send`オブジェクトはグラフ内のノードの名前と
    # そのノードに送信する状態で構成されています

    send_list = []
    for s in state["subjects"]:
        send_list.append(
            Send(
                "generate_joke", # node ( str) – メッセージを送信する対象ノードの名前。
                {"subject":s})   # arg ( Any) – 対象ノードに送信する状態またはメッセージ。
            )

    #return [Send("generate_joke",{"subject":s}) for s in state["subjects"]]
    return send_list
    #    {# coditional edge 
    #        "graph_type":"static_conditional_edge",
    #        "flow_parameter":{
    #            "start_key":"agent",
    #            "conditions":[
    #                {
    #                    "expression": {
    #                        "eq": [{"type": "function", "name": "is_tool_message_function"}, True],
    #                    },
    #                    "result": "tools" # これにfunctionを使えるようにする
    #                              {"type": "function", "name": "is_tool_message_function"}
    #                },
    #                {"default": "END"} # これにfunctionを使えるようにする
    #                            {"type": "function", "name": "is_tool_message_function"}
    #            ]
    #        },
    #    },

# Here we will judge the best joke
# ここで最高のジョークを評価します
def best_joke(state: OverallState):
    jokes = "\n\n".join(state["jokes"])
    prompt = best_joke_prompt.format(topic=state["topic"], jokes=jokes)
    response = model.with_structured_output(BestJoke).invoke(prompt)
    return {"best_selected_joke": state["jokes"][response.id]}

# Construct the graph: here we put everything together to construct our graph
# グラフを構築する：ここでは、すべてをまとめてグラフを構築します
def test_best_joke():
    graph = StateGraph(OverallState)
    graph.add_node("generate_topics", generate_topics)
    graph.add_node("generate_joke", generate_joke)
    graph.add_node("best_joke",best_joke)
    graph.add_edge(START, "generate_topics")
    graph.add_conditional_edges("generate_topics", continue_to_jokes, ["generate_joke"])
    #graph.add_conditional_edges("generate_topics", continue_to_jokes)
    graph.add_edge("generate_joke", "best_joke")
    graph.add_edge("best_joke",END)
    app = graph.compile()

    print(f"\ngraph")
    app.get_graph().print_ascii()

    # Call the graph: here we call it to generate a list of jokes
    for s in app.stream({"topic": "animals"}):
        print(s)


# Send
# グラフ内の特定のノードに送信するメッセージまたはパケット。
#  Sendクラスは、 StateGraphの条件付きエッジ内で使用され、次のステップでカスタム状態を持つノードを動的に呼び出します。
# 重要な点は、送信される状態がコアグラフの状態と異なる場合があり、柔軟で動的なワークフロー管理が可能になることです。
# その一例が「マップ・リデュース」ワークフローで、グラフが異なる状態で同じノードを並行して複数回呼び出し、結果をメイングラフの状態に集約するものです。
# 属性:
# • node ( str) – メッセージを送信する対象ノードの名前。
# • arg ( Any) – 対象ノードに送信する状態またはメッセージ。