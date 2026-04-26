from langchain_core import tools
import logging
import os
import json
import subprocess

logger = logging.getLogger(__name__)


@tools.tool
def execute_aws_sql_query(
    query: str, access_key: str, secret_key: str, aws_region: str = "us-east-1"
) -> str:
    """
    Executes a read-only SQL query against AWS infrastructure to retrieve resource configurations.
    Use this tool ONLY after the SQL query has been validated.
    Returns the results as a JSON string or an error message if the query fails.

    Args:
        query (str): The SQL query to execute.
        access_key (str): AWS access key ID.
        secret_key (str): AWS secret access key.
        aws_region (str): AWS region to execute the query in. Defaults to 'us-east-1'.
    """

    env = os.environ.copy()
    env["AWS_ACCESS_KEY_ID"] = access_key
    env["AWS_SECRET_ACCESS_KEY"] = secret_key
    env["AWS_REGION"] = aws_region

    try:
        exec_result = subprocess.run(
            ["steampipe", "query", query, "--output", "json"],
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )

        result = json.loads(exec_result.stdout)
        return json.dumps(result, indent=2)

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        logger.warning(f"Steampipe SQL Error: {error_msg}")
        return json.dumps({"error": f"SQL execution failed: {error_msg}"})

    except Exception as e:
        logger.error(str(e))
        return json.dumps({"error": str(e)})
