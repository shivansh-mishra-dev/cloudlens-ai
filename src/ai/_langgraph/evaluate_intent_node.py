import logging
from ai.models.gemma4_e2b import gemma4e2b
from ai.agent_state import AgentState
from ai.prompts import EVALUATOR_PROMPT
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)


def evaluate_intent_node(state: AgentState) -> dict:
    """
    LangGraph Node: Expands the user's raw input into a highly detailed AWS intent.
    """

    llm = gemma4e2b()

    user_request = state["messages"][-1].content

    prompt = ChatPromptTemplate.from_template(EVALUATOR_PROMPT)

    chain = prompt | llm
    logger.info("Evaluating and expanding user intent...")
    response = chain.invoke({"request": user_request})

    expanded = str(response.content).strip()

    return {"expanded_intent": expanded}
