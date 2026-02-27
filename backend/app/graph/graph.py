from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END

from backend.app.models.graphState import GraphState, RouteDecision
from .academicGraphNodes import academic_graph, academic_query_node
from .infoGraphNodes import info_graph, rewrite_query_node, retrieve_node, info_query_node
from .adminGraphNodes import admin_graph, admin_leave_node, save_leave_db_node
from ..agents.agentPrompts import get_router_system_prompt
from ..agents.llmBase import LLMBase


async def router_node(state: GraphState):
    messages = state['messages']
    prompt = get_router_system_prompt()
    llm = LLMBase().client
    llm = llm.with_structured_output(RouteDecision)
    decision = await llm.ainvoke([SystemMessage(content=prompt), messages[-1]])
    return {
        "intent": decision.destination
    }


# 定义条件逻辑函数
def route_condition(state: dict):
    # 直接读取 router_node 写入的 intent
    return state["intent"]


_graph = None


def build_graph():
    graph = StateGraph(GraphState)

    nodes = [
        router_node,
        academic_graph, academic_query_node,
        info_graph, rewrite_query_node, retrieve_node, info_query_node,
        admin_graph, admin_leave_node, save_leave_db_node
        ]
    for node in nodes:
        graph.add_node(node.__name__, node)

    graph.add_edge(START, "router_node")
    graph.add_conditional_edges(
        "router_node",
        route_condition,
        {
            "academic": "academic_graph",
            "info": "info_graph",
            "admin": "admin_graph",
            # "chat": "chat_graph"
        }
    )

    # academic子图
    graph.add_edge("academic_graph", "academic_query_node")
    graph.add_edge("academic_query_node", END)
    # info子图
    graph.add_edge("info_graph", "rewrite_query_node")
    graph.add_edge("rewrite_query_node", "retrieve_node")
    graph.add_edge("retrieve_node", "info_query_node")
    graph.add_edge("info_query_node", END)
    # admin子图
    graph.add_edge("admin_graph", "admin_leave_node")
    graph.add_edge("admin_leave_node", END)
    graph.add_edge("save_leave_db_node", END)

    checkpointer = MemorySaver()
    graph = graph.compile(checkpointer=checkpointer)
    return graph


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()

    return _graph
