from langchain_core.runnables import RunnableLambda

# 你的本地模型
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

tokenizer = AutoTokenizer.from_pretrained("../phi3-biostars-merged")
model = AutoModelForCausalLM.from_pretrained("../phi3-biostars-merged")
llm1 = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0)

def phi3_agent(state: dict) -> dict:
    query = state["input"]
    result = llm1(query, max_new_tokens=512)[0]["generated_text"]
    return {"phi3_answer": result}




from typing import Dict
from langchain_core.runnables import RunnableLambda

# 你已经完成的流程：chunks + embeddings + chroma + embedding_model + cross_encoder + gemini_client 都在前面初始化了
from typing import List

def split_into_chunks(doc_file: str) -> List[str]:
    with open(doc_file, 'r',encoding='utf-8') as file:
        content = file.read()
    return [chunk for chunk in content.split("##")]

# 主程序部分
chunks = split_into_chunks("README.md")

# for i, chunk in enumerate(chunks[:5]):
#     print(f"[{i}] {chunk}\n")

from sentence_transformers import SentenceTransformer
from typing import List

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_chunk(chunk: str) -> List[float]:
    embedding = embedding_model.encode(chunk)
    return embedding.tolist()

test_embedding = embed_chunk("test")
# print(len(test_embedding))
# print(test_embedding)

embeddings = [embed_chunk(chunk) for chunk in chunks]
# print(len(embeddings))
# print(embeddings[0])

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


from sentence_transformers import CrossEncoder

def rerank(query:str, retrieved_chunks:List[str],top_k:int) -> List[str]:
    cross_encoder = CrossEncoder('cross-encoder/mmarco-mMiniLMv2-L12-H384-v1')
    pairs=[(query,chunk) for chunk in retrieved_chunks]
    scores=cross_encoder.predict(pairs)

    chunk_with_score_list=[(chunk,score)
                           for chunk,score in zip(retrieved_chunks, scores)]
    chunk_with_score_list.sort(key=lambda pair:pair[1],reverse=True)
    return [chunk for chunk,_ in chunk_with_score_list][:top_k]



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

    # print(f"{prompt}\n\n---\n")

    response = google_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text


def rag_agent(state: Dict[str, str]) -> Dict[str, str]:
    query = state["input"]

    # 检索
    retrieved_chunks = retrieve(query, top_k=5)

    # rerank
    reranked_chunks = rerank(query, retrieved_chunks, top_k=3)

    # 生成答案
    answer = generate(query, reranked_chunks)

    return {"rag_answer": answer}

def reasoning_agent(state: dict) -> dict:
    query = state["input"]
    phi3_answer = state["phi3_answer"]
    rag_answer = state["rag_answer"]

    prompt = f"""Please analyze the following user question and the answers from two agents, and provide a final, concise, and accurate answer in English.
User question:
{query}

phi3_agent's answer:
{phi3_answer}

rag_agent's answer:
{rag_answer}

Please synthesize both answers and output the final answer in English."""
    # Reuse the generate function
    result = generate(query, [phi3_answer, rag_answer])
    return {"final_answer": result}


from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda

# 定义状态类型
from typing import TypedDict

class AgentState(TypedDict):
    input: str
    phi3_answer: str
    rag_answer: str

# 构造状态图

graph = StateGraph(AgentState)
graph.add_node("phi3", phi3_agent)
graph.add_node("rag", rag_agent)
graph.add_node("reasoning", reasoning_agent)
graph.set_entry_point(["phi3", "rag"])
graph.add_edge("phi3", "reasoning")
graph.add_edge("rag", "reasoning")
graph.add_edge("reasoning", END)

# 构建应用
app = graph.compile()
result = app.invoke({"input": "How to use metatdenovo?"})
print(result)

