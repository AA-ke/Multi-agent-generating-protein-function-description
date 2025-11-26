import json
from typing import List

def extract_entry(entry: dict) -> dict:
    """提取单个蛋白的文档信息"""
    doc_id = entry.get("primaryAccession", "UNKNOWN")
    sequence = entry.get("sequence", {}).get("value", "")

    # FUNCTION 注释
    document = ""
    for comment in entry.get("comments", []):
        if comment.get("commentType") == "FUNCTION":
            document = " ".join([t["value"] for t in comment.get("texts", [])])
            break

    # GO 注释
    go_terms, go_descs = [], []
    for xref in entry.get("uniProtKBCrossReferences", []):
        if xref.get("database") == "GO":
            for prop in xref.get("properties", []):
                if prop["key"] == "GoTerm":
                    term = prop["value"]
                    go_terms.append(term.split(":")[0] + ":" + term.split(":")[1])
                    go_descs.append(term.split(":")[1])
                    break

    # Pfam 域
    pfam_ids = [xref["id"] for xref in entry.get("uniProtKBCrossReferences", []) if xref.get("database") == "Pfam"]

    # Gene 名
    gene = entry.get("genes", [{}])[0].get("geneName", {}).get("value", "N/A")

    # Keyword
    keywords = [kw["name"] for kw in entry.get("keywords", [])]

    # 物种
    species = entry.get("organism", {}).get("scientificName", "Unknown")

    return {
        "id": doc_id,
        "sequence": sequence,
        "document": document,
        "metadata": {
            "gene": gene,
            "species": species,
            "go_terms": go_terms,
            "go_descriptions": go_descs,
            "pfam": pfam_ids,
            "functional_keywords": keywords
        }
    }

def extract_documents(json_path: str) -> List[dict]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = data.get("results", [])
    documents = []

    for entry in results:
        try:
            doc = extract_entry(entry)
            documents.append(doc)
        except Exception as e:
            print(f"[ERROR] Failed to parse entry: {entry.get('primaryAccession', 'UNKNOWN')}, Error: {e}")

    return documents


json_file = "./uniprotkb_reviewed_true_AND_model_organ_2025_07_25.json"  # 多蛋白文件路径
all_docs = extract_documents(json_file)

# 保存为文档集合
with open("./uniprot_documents.json", "w", encoding="utf-8") as f:
    json.dump(all_docs, f, indent=2, ensure_ascii=False)

print(f"✅ 提取完成，共 {len(all_docs)} 个蛋白文档")
