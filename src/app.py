import subprocess
import json
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def list_s3_buckets():
    sql_query = f"select name, creation_date from aws_s3_bucket;"

    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = "ap-south-1"

    if not access_key or not secret_key:
        logger.error("NO AWS KEYS FOUND IN .env")
        return

    env = os.environ.copy()
    env["AWS_ACCESS_KEY_ID"] = access_key
    env["AWS_SECRET_ACCESS_KEY"] = secret_key
    env["AWS_REGION"] = aws_region

    try:
        result = subprocess.run(
            ["steampipe", "query", sql_query, "--output", "json"],
            capture_output=True,
            text=True,
            env=env,
            check=True,
        )
        buckets = result.stdout
        logger.info(f"Successfully retrieved {type(buckets)} buckets.")
        return buckets
    except Exception as e:
        logger.error(str(e))
        return


if __name__ == "__main__":
    data = list_s3_buckets()

    if data:
        logger.info(data)
