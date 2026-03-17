# 🚀 Redis-Optimized RAG AI System

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Redis](https://img.shields.io/badge/Redis-Caching-red)
![LLM](https://img.shields.io/badge/LLM-GPT--4o--mini-purple)
![Status](https://img.shields.io/badge/Status-Production--Style-success)

A **production-grade Retrieval Augmented Generation (RAG)** system built using **Redis, FastAPI, FAISS, and OpenAI models**.

This project demonstrates how to design **scalable, cost-efficient AI systems** using real-world backend and infrastructure patterns.

---

## 📌 Overview

This system answers user queries by:

1. Retrieving relevant documents using **semantic search**
2. Generating grounded responses using **LLMs**
3. Optimizing performance using **Redis caching + rate limiting**

---

## 🧠 System Architecture

```

User Question
↓
FastAPI API
↓
Redis Rate Limiter
↓
Redis LLM Cache
↓
Embedding Engine
↓
Redis Embedding Cache
↓
FAISS Vector Search
↓
Context Retrieval
↓
GPT-4o-mini
↓
Cache Response in Redis

```

---

## ⚡ Key Features

### 🧩 Intelligent Caching (Redis)
- Avoids repeated LLM calls using **cache-aside pattern**
- Uses TTL for automatic expiration
- Improves latency + reduces cost

### 🧠 Embedding Cache
- Stores embeddings in Redis
- Prevents redundant API calls
- Speeds up semantic search pipeline

### 🚦 API Rate Limiting
- Built with Redis **atomic counters (INCR + EXPIRE)**
- Protects system from abuse
- Ensures fair usage

### 🔍 Semantic Search
- Uses **FAISS vector similarity search**
- Retrieves top relevant documents
- Improves answer grounding

### 🧠 Retrieval Augmented Generation (RAG)
- Combines:
  - Context retrieval
  - LLM reasoning
- Produces accurate, context-aware responses

### 📊 Observability
- Tracks:
  - Cache hits / misses
  - Embedding usage
  - Rate-limited requests
- Enables system monitoring

### 🌊 Streaming Responses
- Token-level streaming from LLM
- Improves perceived performance

---

## 🧱 Redis Design Patterns Used

| Feature | Implementation |
|--------|--------|
| LLM Cache | Cache-aside (`SETEX`) |
| Embedding Cache | Key-based lookup |
| Rate Limiting | `INCR + EXPIRE` |
| Metrics | Redis counters |
| TTL Expiration | Automatic refresh |

---

## 🛠️ Tech Stack

### Backend
- Python 3.12
- FastAPI
- Uvicorn

### AI / ML
- OpenAI Embeddings
- GPT-4o-mini
- FAISS Vector Search

### Infrastructure
- Redis
- python-dotenv

---

## 📁 Project Structure

```

redis-rag-ai-system
│
├── app
│   ├── main.py              # FastAPI entrypoint
│   ├── cache.py            # LLM caching logic
│   ├── rate_limiter.py     # Redis rate limiting
│   ├── embeddings.py       # Embedding generation + caching
│   ├── vector_search.py    # FAISS search
│   ├── rag_pipeline.py     # Core RAG logic
│   └── redis_client.py     # Redis connection
│
├── data
│   └── documents.txt       # Knowledge base
│
├── requirements.txt
├── .env.example
└── README.md

````

---

## 🌐 API Endpoints

### ✅ Health Check

```http
GET /health
````

Checks system + Redis connectivity.

---

### 🤖 Ask Question (RAG)

```http
GET /ask?question=What is Redis?
```

#### Example Response

```json
{
  "source": "llm",
  "remaining_requests": 4,
  "data": {
    "answer": "Redis is an in-memory data structure store used as a database, cache, and message broker."
  }
}
```

---

### 🌊 Streaming Response

```http
GET /stream?question=What is Redis?
```

Streams tokens in real-time.

---

### 📊 Metrics

```http
GET /metrics
```

#### Example

```json
{
  "cache_hits": 10,
  "cache_misses": 3,
  "embedding_cache_hits": 25,
  "embedding_cache_misses": 5,
  "rate_limited_requests": 2
}
```

---

## ⚙️ Running the Project

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 2. Setup Environment Variables

Create `.env`

```env
OPENAI_API_KEY=your_openai_api_key
```

---

### 3. Start Redis

```bash
redis-server
```

---

### 4. Run the API

```bash
uvicorn app.main:app --reload
```

---

### 5. Open API Docs

```
http://127.0.0.1:8000/docs
```

---

## 🔄 Example Flow

For:

```http
GET /ask?question=What is Redis?
```

The system:

1. Checks Redis cache
2. Applies rate limiting
3. Generates embedding
4. Searches via FAISS
5. Retrieves context
6. Calls GPT-4o-mini
7. Caches response
8. Returns answer

---

## 🎯 Why This Project Matters

This project demonstrates **real-world AI system design skills**:

* ✅ LLM cost optimization using caching
* ✅ Scalable backend architecture
* ✅ Efficient retrieval pipelines (RAG)
* ✅ Production-grade rate limiting
* ✅ Observability & metrics tracking

These are **core skills required for ML / AI / Backend roles**.

---

## 🚀 Future Improvements

* Redis Vector Search (replace FAISS)
* Dockerized deployment
* Web UI (chat interface)
* Distributed Redis cluster
* Advanced RAG (re-ranking, chunking strategies)

---

## 👨‍💻 Author

**Pavan Kumar**

* AI / ML Engineer
* Focus: LLM Systems, Backend AI, Production ML

---

## ⭐ If You Like This Project

Give it a star ⭐ and feel free to fork & build on it!
