import hashlib
import json
import os
from dotenv import load_dotenv
from app.redis_client import redis_client
import re

load_dotenv()

CACHE_TTL = os.getenv("CACHE_TTL")

def normalize_query(query: str) -> str:
    query = query.lower().strip()
    query = re.sub(r"[^\w\s]", "", query)
    query = re.sub(r"\s+", " ", query)
    return query

def generate_cache_key(prompt:str) -> str:
    """
    Generate a unique cache key for a prompt.
    """
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
    return f"llm_cache:{prompt_hash}"

def get_cached_response(prompt: str) -> str:
    """
    Check Redis for cached response.
    """
    key = generate_cache_key(prompt)
    cached = redis_client.get(key)
    if cached:
        redis_client.incr("cache_hits")
        return json.loads(cached)
    redis_client.incr("cache_misses")
    return None

def cache_response(prompt: str, response: dict):
    """
    Store response in Redis with TTL.
    """
    key = generate_cache_key(prompt)

    redis_client.setex(
        key,
        CACHE_TTL,
        json.dumps(response)
    )