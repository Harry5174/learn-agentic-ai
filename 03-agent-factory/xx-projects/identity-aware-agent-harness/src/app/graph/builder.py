from langgraph.graph import END, START, StateGraph

from app.graph.nodes import (
    execute_tool,
    finalize_denial,
    generate_report,
    interpret_task,
    pause_for_approval,
    policy_guard,
)
from app.graph.routing import route_after_interpret_task, route_after_policy_guard
from app.graph.state import HarnessGraphState


def build_harness_graph():
    """Build the local LangGraph harness.

    This graph is local-only:
    - no FastAPI
    - no checkpoint persistence
    - no LLM
    - no external calls
    """

    builder = StateGraph(HarnessGraphState)

    builder.add_node("interpret_task", interpret_task)
    builder.add_node("policy_guard", policy_guard)
    builder.add_node("execute_tool", execute_tool)
    builder.add_node("finalize_denial", finalize_denial)
    builder.add_node("pause_for_approval", pause_for_approval)
    builder.add_node("generate_report", generate_report)

    builder.add_edge(START, "interpret_task")

    builder.add_conditional_edges(
        "interpret_task",
        route_after_interpret_task,
        {
            "policy_guard": "policy_guard",
            "generate_report": "generate_report",
        },
    )

    builder.add_conditional_edges(
        "policy_guard",
        route_after_policy_guard,
        {
            "execute_tool": "execute_tool",
            "finalize_denial": "finalize_denial",
            "pause_for_approval": "pause_for_approval",
            "generate_report": "generate_report",
        },
    )

    builder.add_edge("execute_tool", "generate_report")
    builder.add_edge("finalize_denial", END)
    builder.add_edge("pause_for_approval", END)
    builder.add_edge("generate_report", END)

    return builder.compile()