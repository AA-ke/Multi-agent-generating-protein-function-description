from typing import List

def split_into_chunks(doc_file: str) -> List[str]:
    with open(doc_file, 'r',encoding='utf-8') as file:
        content = file.read()
    return [chunk for chunk in content.split("##")]

# 主程序部分
chunks = split_into_chunks("README.md")

for i, chunk in enumerate(chunks[:5]):
    print(f"[{i}] {chunk}\n")

from sentence_transformers import SentenceTransformer
from typing import List

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_chunk(chunk: str) -> List[float]:
    embedding = embedding_model.encode(chunk)
    return embedding.tolist()

test_embedding = embed_chunk("test")
print(len(test_embedding))
print(test_embedding)

embeddings = [embed_chunk(chunk) for chunk in chunks]
print(len(embeddings))
print(embeddings[0])

import chromadb

chromadb_client = chromadb.EphemeralClient()
chromadb_collection = chromadb_client.get_or_create_collection(name="default")

def save_embeddings(chunks:List[str], embeddings:List[List[float]]) -> None:
    ids = [str(i) for i in range(len(chunks))]
    chromadb_collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids
    )

save_embeddings(chunks,embeddings)

def retrieve(query: str, top_k: int) -> List[str]:
    query_embedding = embed_chunk(query)
    results = chromadb_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "distances"]  # 建议带上距离，方便观察
    )
    return results['documents'][0]

# 测试
query = "What is metatdenovo?How to use it?"
retrieved_chunks = retrieve(query, 5)

for i, chunk in enumerate(retrieved_chunks):
    print(f"[{i}] {chunk}\n")

from sentence_transformers import CrossEncoder

def rerank(query:str, retrieved_chunks:List[str],top_k:int) -> List[str]:
    cross_encoder = CrossEncoder('cross-encoder/mmarco-mMiniLMv2-L12-H384-v1')
    pairs=[(query,chunk) for chunk in retrieved_chunks]
    scores=cross_encoder.predict(pairs)

    chunk_with_score_list=[(chunk,score)
                           for chunk,score in zip(retrieved_chunks, scores)]
    chunk_with_score_list.sort(key=lambda pair:pair[1],reverse=True)
    return [chunk for chunk,_ in chunk_with_score_list][:top_k]

reranked_chunks = rerank(query, retrieved_chunks,3)

for i,chunk in enumerate(reranked_chunks):
    print(f"[{i}]{chunk}\n")

from dotenv import load_dotenv
from google import genai


load_dotenv()
google_client = genai.Client()

def generate(query: str, chunks: List[str]) -> str:
    relevant_info = "\n\n".join(chunks)

    prompt = f"""You're a knowledge assistant, please answer questions according to the user's request and the following information.

User's question:
{query}

Relevant information:
{relevant_info}

Please answer according to the information mentioned above. Do not make up information."""

    print(f"{prompt}\n\n---\n")

    response = google_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text


answer = generate(query,reranked_chunks)
print(answer)

