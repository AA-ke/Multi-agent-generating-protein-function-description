import requests
import pandas as pd
from tqdm import tqdm

def fetch_uniprot_json(query, size=1000):
    base_url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": query,
        "format": "json",
        "fields": "accession,sequence,comment(FUNCTION)",
        "size": 500
    }

    fetched = 0
    all_data = []
    pbar = tqdm(total=size, desc="Downloading JSON records")

    while fetched < size:
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print("Request failed:", response.status_code)
            break

        data = response.json()
        results = data.get("results", [])
        if not results:
            print("No more results.")
            break

        for entry in results:
            seq = entry.get("sequence", {}).get("value")
            if not seq:
                continue

            func = "功能未知"
            if "comments" in entry:
                for comment in entry["comments"]:
                    if comment["commentType"] == "FUNCTION":
                        func_texts = [t["value"] for t in comment["texts"]]
                        func = " ".join(func_texts)
                        break

            all_data.append({
                "protein_sequence": seq,
                "function_description": func
            })
            fetched += 1
            pbar.update(1)

            if fetched >= size:
                break

        # 翻页
        links = response.headers.get("Link")
        if not links:
            break

        next_url = None
        for link in links.split(","):
            if 'rel="next"' in link:
                next_url = link[link.find("<")+1:link.find(">")]
                break

        if next_url:
            base_url = next_url
            params = {}  # next链接自带所有参数，清空原params
        else:
            break

    pbar.close()
    return all_data


if __name__ == "__main__":
    query = "reviewed:true AND organism_id:9606"  # 改这里自定义筛选条件
    data = fetch_uniprot_json(query, size=1000)

    # 保存成 CSV
    df = pd.DataFrame(data)
    df.to_csv("train.csv", index=False, encoding="utf-8")
    print(f"✅ 共抓取 {len(df)} 条，已保存 train.csv")

    # 同时也可以保存成 JSONL
    with open("train.jsonl", "w", encoding="utf-8") as f:
        for item in data:
            f.write(f"{item}\n")
    print("✅ 同步保存 train.jsonl")
