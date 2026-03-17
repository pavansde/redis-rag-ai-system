import faiss
import numpy as np
from app.embeddings import generate_embeddings

documnets = []
index = None

def load_documents(file_path = "data/documents.txt"):
    global documents
    with open(file_path, "r") as f:
        documents = [line.strip() for line in f if line.strip()]

def build_index():
    global index

    embeddings = []

    for doc in documents:
        vector = generate_embeddings(doc)
        embeddings.append(vector)

    vectors = np.array(embeddings).astype("float32")

    dimension = vectors.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)


def search_documents(query, top_k=2):
    query_vector = generate_embeddings(query)

    query_vector = np.array([query_vector]).astype("float32")

    distances, indices = index.search(query_vector, top_k)

    results = []

    for idx in indices[0]:
        results.append(documents[idx])

    return results