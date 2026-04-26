from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from ai.agent_state import AgentState
from ai._langgraph.evaluate_intent_node import evaluate_intent_node
from ai._langgraph.guardrail_node import guardrail_node
from ai._langgraph.generate_sql_node import generate_sql_node
from ai._langgraph.validate_sql_node import validate_sql_node
from ai._langgraph.execute_sql_node import execute_sql_node
from ai._langgraph.format_response_node import format_response_node
import logging

logger = logging.getLogger(__name__)


def route_after_validation(state: AgentState) -> str:
    """
    Conditional edge routing logic.
    Inspects the state to determine if the SQL needs correction.
    """
    if state.get("error_message"):
        logger.warning("Routing back to CodeGenerator for self-correction...")
        return "generate"

    logger.info("Validation passed. Proceeding to next step.")
    return "execute"


def route_after_guardrail(state: AgentState) -> str:
    """
    Conditional edge routing logic for the gateway.
    Short-circuits the graph if the query is unrelated to AWS infrastructure.
    """
    if state.get("is_infra_query"):
        logger.info("Guardrail passed. Proceeding to Code Generation.")
        return "generate"

    logger.warning("Guardrail failed. Short-circuiting to Response Formatter.")
    return "format"


def build_agent_graph():
    """
    Builds and returns the agent graph for SQL query generation and validation.

    Returns:3
        CompiledStateGraph: The configured StateGraph object representing the agent workflow.
    """
    builder = StateGraph(AgentState)
    memory = MemorySaver()

    builder.add_node("evaluate", evaluate_intent_node)
    builder.add_node("guardrail", guardrail_node)
    builder.add_node("generate", generate_sql_node)
    builder.add_node("validate", validate_sql_node)
    builder.add_node("execute", execute_sql_node)
    builder.add_node("format", format_response_node)

    builder.add_edge(START, "evaluate")
    builder.add_edge("evaluate", "guardrail")

    builder.add_conditional_edges(
        "guardrail", route_after_guardrail, {"generate": "generate", "format": "format"}
    )
    builder.add_edge("generate", "validate")

    builder.add_conditional_edges(
        "validate",
        route_after_validation,
        {"generate": "generate", "execute": "execute"},
    )

    builder.add_edge("execute", "format")
    builder.add_edge("format", END)
    graph = builder.compile(checkpointer=memory)

    return graph
