import os
from dotenv import load_dotenv
from openai import OpenAI
from app.vector_search import search_documents

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def build_prompt(question: str, docs: list[str]):

    context = "\n".join(docs)

    prompt = f"""
Use ONLY the following context to answer the question.

If the answer cannot be found in the context, say you don't know.

Context:
{context}

Question:
{question}

Answer clearly and concisely.
"""

    return prompt


# -----------------------------
# Synchronous RAG (existing)
# -----------------------------

def generate_answer(question: str):

    docs = search_documents(question)

    prompt = build_prompt(question, docs)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return {
        "answer": response.choices[0].message.content,
        "context_used": docs
    }


# -----------------------------
# Streaming RAG
# -----------------------------

def stream_rag_answer(question: str):

    docs = search_documents(question)

    prompt = build_prompt(question, docs)

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        stream=True
    )

    full_answer = ""

    for chunk in stream:

        delta = chunk.choices[0].delta

        if delta and delta.content:
            token = delta.content
            full_answer += token
            yield token

    return full_answer, docs