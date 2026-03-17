import os
import json
import hashlib
from app.redis_client import redis_client
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))
EMBEDDING_CACHE_TTL = 86400 # 24hrs


def generate_embedding_key(text: str):
    """
    Generate Redis key for embedding cache
    """
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    return f"embedding:{text_hash}"

def generate_embeddings(text: str):
    """
    Generate vector embedding for text using OpenAI.
    """
    key = generate_embedding_key(text)
    cached = redis_client.get(key)
    if cached:
        redis_client.incr("embedding_cache_hits")
        return json.loads(cached)
    redis_client.incr("embedding_cache_misses")
    response = client.embeddings.create(
        model = "text-embedding-3-small",
        input = text
    )
    embeddings = response.data[0].embedding
    redis_client.setex(
        key,
        EMBEDDING_CACHE_TTL,
        json.dumps(embeddings)
    )
    return embeddings