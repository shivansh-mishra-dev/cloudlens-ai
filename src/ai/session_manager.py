import redis
import json
import logging
from typing import Tuple, Optional, cast

logger = logging.getLogger(__name__)


REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = "RedisPass032"


try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True,
        db=0,
    )

    redis_client.ping()
    logger.info("Successfully connected to redis client.")
except redis.ConnectionError as re:
    logger.error(f"Failed to connect to redis : {re}")
    redis_client = None


def cache_aws_credentials(session_id: str, access_key: str, secret_key: str):
    """
    Stores AWS credentials in Redis with a strict 15-minute (900 seconds) TTL.
    """

    if not redis_client:
        return False

    cache_key = f"aws_session:{session_id}"
    payload = json.dumps({"access_key": access_key, "secret_key": secret_key})

    try:
        redis_client.set(name=cache_key, value=payload, ex=900)
        logger.info(f"Credentials cached successfully for session: {session_id}")
        return True
    except redis.RedisError as e:
        logger.error(f"Redis caching error: {e}")
        return False


def get_aws_credentials(session_id: str):
    """
    Retrieves temporary AWS credentials from Redis.
    Returns (access_key, secret_key) or (None, None) if expired/missing.
    """

    if not redis_client:
        return (
            None,
            None,
        )

    cache_key = f"aws_session:{session_id}"
    try:
        raw_data = redis_client.get(cache_key)
        data = cast(Optional[str], raw_data)
        if data:
            creds = json.loads(data)
            return creds.get("access_key"), creds.get("secret_key")
        else:
            logger.warning(f"Session {session_id} expired or not found in Redis.")
            return None, None
    except redis.RedisError as e:
        logger.error(f"Redis retrieval error: {e}")
        return None, None
