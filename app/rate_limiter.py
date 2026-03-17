import os
from dotenv import load_dotenv
from app.redis_client import redis_client

load_dotenv()

RATE_LIMIT = int(os.getenv("RATE_LIMIT"))
WINDOW = 60 # seconds

def check_rate_limit(ip: str):
    """
    Production-grade rate limiter.

    Returns:
        allowed (bool)
        remaining_requests (int)
        retry_after (seconds)
    """
    key = f"rate_limit:{ip}"
    request_count = redis_client.incr(key)

    if request_count == 1:
        redis_client.expire(key, WINDOW)

    ttl = redis_client.ttl(key)
    
    if request_count > RATE_LIMIT:
        redis_client.incr("rate_limited_requests")
        return {
            "allowed": False,
            "remaining": 0,
            "retry_after": ttl
        }

    remaining = RATE_LIMIT - request_count
    return {
            "allowed": True,
            "remaining": remaining,
            "retry_after": ttl
        }
    