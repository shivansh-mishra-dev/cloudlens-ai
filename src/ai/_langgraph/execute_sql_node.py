import logging
import json
from ai.agent_state import AgentState
from ai.tools.execute_aws_sql_query import execute_aws_sql_query
from ai.session_manager import get_aws_credentials

logger = logging.getLogger(__name__)


def execute_sql_node(state: AgentState) -> dict:
    """
    LangGraph Node: Execute the validated SQL query against steampipe.
    """

    sql = state.get("sql_query")
    session_id = state.get("session_id")

    logger.info(f"Preparing to execute SQL for session : {session_id}")

    aws_access_key, aws_secret_key = get_aws_credentials(session_id)

    raw_json_result = execute_aws_sql_query.invoke(
        {
            "query": sql,
            "access_key": aws_access_key,
            "secret_key": aws_secret_key,
            "aws_region": "ap-south-1",
        }
    )

    try:
        parsed_result = json.loads(raw_json_result)
        if "error" in parsed_result:
            logger.error(f"Error executing SQL: {parsed_result['error']}")
            return {"error_message": parsed_result["error"]}

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse execution result as JSON: {e}")
        return {"error_message": f"Failed to parse Steampipe JSON output : {str(e)}"}

    logger.info(f"SQL executed successfully for session : {session_id}")

    return {"raw_data": raw_json_result, "error_message": None}
