import chromadb
from chromadb.config import Settings
import json

# 初始化 Chroma
client = chromadb.Client(Settings())
collection = client.get_or_create_collection(name="proteins")

# 加载文档
with open("Agents/uniprot_documents_with_embedding.json", "r", encoding="utf-8") as f:
    docs = json.load(f)

# 添加到数据库
def flatten_metadata(meta):
    new_meta = {}
    for k, v in meta.items():
        if isinstance(v, list):
            new_meta[k] = ", ".join(map(str, v))
        else:
            new_meta[k] = v
    return new_meta

collection.add(
    documents=[doc["document"] for doc in docs],
    metadatas=[flatten_metadata(doc["metadata"]) for doc in docs],
    ids=[doc["id"] for doc in docs],
    embeddings=[doc["embedding"] for doc in docs]
)


from esm import pretrained
import torch
import numpy as np

# 加载模型
model, alphabet = pretrained.esm2_t33_650M_UR50D()
batch_converter = alphabet.get_batch_converter()
model.eval()

def embed_sequence(seq):
    batch_labels, batch_strs, batch_tokens = batch_converter([("query", seq)])
    with torch.no_grad():
        results = model(batch_tokens, repr_layers=[33])
    embedding = results["representations"][33][0, 1:len(seq)+1].mean(0).cpu().numpy()
    return embedding.tolist()

def query_rag(seq, top_k=3):
    emb = embed_sequence(seq)
    results = collection.query(
        query_embeddings=[emb],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    return results

query_seq = "MFRRLTFAQLLFATVLGIAGGVYIFQPVFEQYAKDQKELKEKMQLVQESEEKKS"
result = query_rag(query_seq, top_k=3)
print("实际返回结果数：", len(result['documents'][0]))
for i in range(len(result['documents'][0])):
    doc = result['documents'][0][i]
    meta = result['metadatas'][0][i]
    distance = result['distances'][0][i]
    print("功能描述：", doc)
    print("元数据：", meta)
    print("距离：", distance)
    print("-"*100)

from dotenv import load_dotenv
from google import genai


load_dotenv()
google_client = genai.Client()

def generate(query_seq, retrieved_docs) -> str:
    relevant_info = retrieved_docs["documents"][0]

    prompt = f"""
    你是一名蛋白质功能注释专家，请根据以下蛋白序列，再根据相似蛋白的相关注释内容进行功能预测：

    用户输入序列：
    {query_seq}

    相似蛋白的相关注释内容：
    {relevant_info}

    总结此蛋白可能的功能、参与的通路、结构域和潜在疾病联系。
    """

    print(f"{prompt}\n\n---\n")

    response = google_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text


answer = generate(query_seq,result)
print(answer)


