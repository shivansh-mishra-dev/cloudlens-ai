from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from ai.prompts import GENERATOR_SYSTEM_PROMPT
from ai.agent_state import AgentState
from ai.models.gemma4_e2b import gemma4e2b
import logging
import re

logger = logging.getLogger(__name__)


def _clean_sql(raw_response: str) -> str:
    """
    Extracts the SQL from the CoT response using regex.
    """
    match = re.search(r"<sql>(.*?)</sql>", raw_response, re.DOTALL | re.IGNORECASE)
    sql = match.group(1).strip() if match else raw_response.strip()

    if sql.startswith("```sql"):
        sql = sql[6:]
    if sql.startswith("```"):
        sql = sql[3:]
    if sql.endswith("```"):
        sql = sql[:-3]

    return sql.strip()


def generate_sql_node(state: AgentState):
    """
    LangGraph Node: Generates a Steampipe SQL query based on user intent.
    If an error message exists in the state, it attempts to fix the previous query.
    """
    llm = gemma4e2b()
    WINDOW_SIZE = 5
    recent_messages = list(state["messages"][-WINDOW_SIZE:])

    if state.get("expanded_intent"):
        recent_messages[-1] = HumanMessage(content=state["expanded_intent"])

    error_context = ""
    if state.get("error_message"):
        error_context = (
            f"\nThe previous query failed with error:\n"
            f"{state['error_message']}\n"
            f"Please correct the SQL query to resolve this issue."
        )

        recent_messages.append(HumanMessage(content=error_context))

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", GENERATOR_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
        ]
    )

    chain = prompt | llm
    logger.info("Invoking local LLM to generate Steampipe SQL...")

    response = chain.invoke({"chat_history": recent_messages})

    content = response.content
    if isinstance(content, list):
        content = " ".join([str(item) for item in content])

    raw_sql = str(content).strip()
    cleaned_sql = _clean_sql(raw_sql)

    return {"sql_query": cleaned_sql, "error_message": None}
