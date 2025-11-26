import chromadb
from chromadb.config import Settings
import json

# 初始化 Chroma
client = chromadb.Client(Settings())
collection = client.get_or_create_collection(name="proteins")

# 加载文档
with open("Agents/uniprot_documents_with_embedding copy.json", "r", encoding="utf-8") as f:
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

def calculate_sequence_confidence(query_seq, retrieved_docs) -> float:
    """
    计算序列分析的置信度
    
    Args:
        query_seq: 查询序列
        retrieved_docs: 检索到的文档
    
    Returns:
        置信度分数 (0-1)
    """
    try:
        distances = retrieved_docs.get("distances", [[]])[0]
        documents = retrieved_docs.get("documents", [[]])[0]
        if not distances or not isinstance(distances, list):
            return 0.5

        # 1) 最小距离分数（越小越好）
        d_min = float(np.min(distances))
        if d_min <= 0.0:
            min_score = 0.95
        elif d_min < 0.2:
            min_score = 0.90
        elif d_min < 0.5:
            min_score = 0.80
        elif d_min < 1.0:
            min_score = 0.60
        else:
            min_score = 0.40

        # 2) 平均距离分数（整体相似度，假设距离0-2范围线性映射）
        d_avg = float(np.mean(distances))
        avg_score = max(0.0, min(1.0, 1.0 - d_avg / 2.0))

        # 3) 前两名间隔（margin）分数：第一名领先幅度
        sorted_d = sorted(float(x) for x in distances)
        if len(sorted_d) >= 2:
            margin = max(0.0, sorted_d[1] - sorted_d[0])
            margin_score = max(0.0, min(1.0, margin / 0.5))  # ≥0.5 视为满分
        else:
            margin_score = 0.6

        # 4) 命中数量分数：命中越多越稳定（最多按3计）
        hits = len(distances)
        hits_score = max(0.0, min(1.0, hits / 3.0))

        # 组合权重（偏重最小距离，其次平均距离与领先幅度）
        confidence = (
            min_score * 0.5 +
            avg_score * 0.25 +
            margin_score * 0.15 +
            hits_score * 0.10
        )
        return float(max(0.0, min(1.0, confidence)))
    except Exception as e:
        print(f"Warning: Error calculating sequence confidence: {e}")
        return 0.5  # 默认中等置信度

from dotenv import load_dotenv
from google import genai

load_dotenv()
google_client = genai.Client()

def generate(query_seq, retrieved_docs) -> str:
    docs = retrieved_docs.get("documents", [[]])[0]
    dists = retrieved_docs.get("distances", [[]])[0]
    lines = []
    for i, doc in enumerate(docs):
        dist = dists[i] if i < len(dists) else None
        dist_str = f"{dist:.4f}" if isinstance(dist, (int, float, float)) else "NA"
        lines.append(f"[{i+1}] distance={dist_str}\n{doc}")
    relevant_info = "\n\n".join(lines) if lines else "(no retrievals)"
    prompt = f"""
    You are a protein sequence information expert. Please provide a functional prediction based on the following protein sequence and related annotations from similar proteins:

    User input sequence:
    {query_seq}

    Related annotations from similar proteins:
    {relevant_info}

   Please generate a comprehensive, accurate, and fluent natural language functional description from three aspects:
    1. Molecular Function (MF) - Biochemical activity of the protein
    2. Biological Process (BP) - Biological processes the protein participates in
    3. Cellular Component (CC) - Cellular localization of the protein

    Please provide detailed and accurate functional descriptions, including:
    - Main functional characteristics
    - Possible biological roles
    - Related metabolic pathways
    - Potential disease associations
    - Domain and functional site analysis
    
    """

    response = google_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

def sequence_agent(state: dict) -> dict:
    seq = state["input"]
    result = query_rag(seq, top_k=3)
    sequence_nl = generate(seq, result)
    sequence_confidence = calculate_sequence_confidence(seq, result)
    
    return {
        "sequence_nl": sequence_nl,
        "sequence_confidence": sequence_confidence
    }

