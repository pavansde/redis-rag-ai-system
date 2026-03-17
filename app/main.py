from fastapi import FastAPI, Request
from app.cache import get_cached_response, cache_response, normalize_query
from app.rate_limiter import check_rate_limit
from app.vector_search import load_documents, build_index
from app.rag_pipeline import generate_answer, stream_rag_answer
from app.redis_client import redis_client
from fastapi.responses import StreamingResponse
from openai import OpenAI
import os

app = FastAPI(title="Redis RAG AI System")
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

@app.on_event("startup")
def startup_event():
    load_documents()
    build_index()

@app.get("/")
def root():
    return {
        "service": "Redis RAG AI System",
        "status": "running"
    }

@app.get("/health")
def health():

    try:
        redis_client.ping()
        redis_status = "connected"
    except Exception:
        redis_status = "disconnected"

    return {
        "status": "ok",
        "redis": redis_status,
        "service": "redis-rag-ai-system"
    }


@app.get("/ask")
def ask(question: str, request: Request):
    client_ip = request.client.host
    rate = check_rate_limit(client_ip)

    if not rate["allowed"]:
        return {
            "error": "Rate limit exceeded",
            "retry_after": rate["retry_after"]
        }
    
    normalized = normalize_query(question)
    cached = get_cached_response(normalized)
    if cached:
        return {
            "source": "cache",
            "remaining_requests": rate["remaining"],
            "data": cached
        }
    result = generate_answer(question)

    cache_response(question, result)
    return {
        "source": "llm",
        "remaining_requests": rate["remaining"],
        "data": result
    }

@app.get("/metrics")
def metrics():

    return {
        "cache_hits": int(redis_client.get("cache_hits") or 0),
        "cache_misses": int(redis_client.get("cache_misses") or 0),
        "embedding_cache_hits": int(redis_client.get("embedding_cache_hits") or 0),
        "embedding_cache_misses": int(redis_client.get("embedding_cache_misses") or 0),
        "rate_limited_requests": int(redis_client.get("rate_limited_requests") or 0)
    }

@app.get("/stream")
def stream_answer(question: str, request: Request):

    # -----------------------------
    # Rate Limiting
    # -----------------------------

    client_ip = request.client.host

    rate = check_rate_limit(client_ip)

    if not rate["allowed"]:
        return {
            "error": "Rate limit exceeded",
            "retry_after": rate["retry_after"]
        }

    # -----------------------------
    # Redis Cache Check
    # -----------------------------

    normalized = normalize_query(question)
    cached = get_cached_response(normalized)

    if cached:

        def cached_stream():
            yield "__SOURCE__:cache\n"
            yield cached["answer"]

        return StreamingResponse(cached_stream(), media_type="text/plain")

    # -----------------------------
    # Streaming RAG (Cache Miss)
    # -----------------------------

    def event_stream():

        full_answer = ""

        yield "__SOURCE__:llm\n"

        for token in stream_rag_answer(question):
            full_answer += token
            yield token
        normalized = normalize_query(question)
        # Store final response in Redis
        cache_response(normalized, {
            "answer": full_answer,
            "context_used": []
        })

    return StreamingResponse(event_stream(), media_type="text/plain")