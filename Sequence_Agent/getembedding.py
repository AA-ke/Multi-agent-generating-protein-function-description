import json
import torch
from tqdm import tqdm
import esm

# 加载 ESM-2 模型
model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()  # 1280维
batch_converter = alphabet.get_batch_converter()
model.eval()

def compute_embedding(sequence: str) -> list:
    batch_labels, batch_strs, batch_tokens = batch_converter([("protein", sequence)])
    batch_tokens = batch_tokens  

    with torch.no_grad():
        results = model(batch_tokens, repr_layers=[33], return_contacts=False)
    token_embeddings = results["representations"][33]

    embedding = token_embeddings[0, 1:len(sequence)+1].mean(0).cpu().numpy()
    return embedding.tolist()



with open("./uniprot_documents.json", "r", encoding="utf-8") as f:
    docs = json.load(f)


docs = docs[:1000]

for doc in tqdm(docs):
    seq = doc.get("sequence", "")
    if seq:
        try:
            doc["embedding"] = compute_embedding(seq)
        except Exception as e:
            print(f"[ERROR] {doc['id']}: {e}")
            doc["embedding"] = []


with open("./uniprot_documents_with_embedding.json", "w", encoding="utf-8") as f:
    json.dump(docs, f, indent=2, ensure_ascii=False)

print(f"✅ 成功为 {len(docs)} 个蛋白生成 embedding")
