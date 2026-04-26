import logging
import re
from ai.agent_state import AgentState


logger = logging.getLogger(__name__)


def validate_sql_node(state: AgentState) -> dict:
    """
    LangGraph Node: Validates the generated SQL query for syntax and safety.
    Ensure the generated query is safe and only performs read-only operation.
    """

    sql = state.get("sql_query", "")

    if not sql:
        return {"error_message": "Vaildation failed : No SQL query was generated."}

    upper_sql = sql.upper().strip()

    if not upper_sql.startswith("SELECT"):
        logger.warning(f"Non-SELECT SQL query detected: {sql}")
        return {
            "error_message": f"Validation failed: Only SELECT queries are allowed. Non-Select Query blocket -> {sql}"
        }

    forbidden_keywords = [
        "DROP",
        "DELETE",
        "INSERT",
        "UPDATE",
        "CREATE",
        "ALTER",
        "EXECUTE",
        "CALL",
        "TRUNCATE",
        "REPLACE",
    ]
    for word in forbidden_keywords:
        if re.search(rf"\b{word}\b", upper_sql):
            logger.warning(f"Forbidden SQL keyword '{word}' found in query: {sql}")
            return {
                "error_message": f"Validation failed: Security Violation! The keyword '{word}' is strictly prohibited. Please generate a read-only query."
            }

    logger.info("SQL Validation Passed : Query is safe for execution.")
    return {"error_message": None}
