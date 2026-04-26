import logging
from ai.models.gemma4_e2b import gemma4e2b
from ai.agent_state import AgentState
from ai.prompts import GUARDRAIL_PROMPT
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)


def guardrail_node(state: AgentState) -> dict:
    """
    LangGraph Node: Ensures the user's request is about AWS infrastructure.
    """

    llm = gemma4e2b()
    expanded_intent = state.get("expanded_intent", state["messages"][-1].content)

    prompt = ChatPromptTemplate.from_template(GUARDRAIL_PROMPT)
    chain = prompt | llm

    logger.info("Applying guardrail check...")
    response = chain.invoke({"request": expanded_intent})
    result = str(response.content).strip().upper()

    is_valid = "TRUE" in result
    print(f"\n[DEBUG] Expanded Intent: {expanded_intent}")
    print(f"[DEBUG] Guardrail Raw LLM Output: {response}\n")

    if not is_valid:
        logger.warning("Guardrail triggered: Non-infrastructure query detected.")
        return {
            "is_infra_query": False,
            "error_message": "I can only answer questions related to your AWS infrastructure configuration.",
        }

    return {"is_infra_query": True}
