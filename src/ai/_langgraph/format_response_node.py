from ai.models.gemma4_e2b import gemma4e2b
from langchain_core.messages import AIMessage
from ai.agent_state import AgentState
from ai.prompts import FORMATTER_SYSTEM_PROMPT
from langchain_core.prompts import ChatPromptTemplate
import logging

logger = logging.getLogger(__name__)


def format_response_node(state: AgentState) -> dict:
    """
    LangGraph Node: Synthesizes the raw Steampipe JSON into a human-readable AIMessage.
    """
    print(f"\n[DEBUG] Formatter received state: {state.keys()}")
    print(f"[DEBUG] Error Message in state: {state.get('error_message')}\n")
    logger.info("Formatting final response...")
    llm = gemma4e2b()

    user_request = state["messages"][-1].content
    raw_data = state.get("raw_data")
    error_message = state.get("error_message")

    if error_message:
        fallback_msg = f"I encountered an issue while trying to query your AWS environment: {error_message}"
        return {"messages": [AIMessage(content=fallback_msg)]}

    if not raw_data or raw_data == "{}":
        empty_msg = "The query executed successfully, but no matching AWS resources were found in your account."
        return {"messages": [AIMessage(content=empty_msg)]}

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", FORMATTER_SYSTEM_PROMPT),
            ("human", "User Question: {request}\n\nAWS JSON Data:\n{data}"),
        ]
    )

    chain = prompt | llm

    try:
        response = chain.invoke({"request": user_request, "data": raw_data})

        return {"messages": [AIMessage(content=str(response.content).strip())]}

    except Exception as e:
        logger.error(f"Formatting failed: {str(e)}")
        error_msg = "I retrieved your data successfully, but ran into an error formatting the response."
        return {"messages": [AIMessage(content=error_msg)]}
