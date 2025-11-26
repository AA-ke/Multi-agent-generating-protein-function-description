import torch
from transformers import AutoTokenizer, AutoModel
from goatools.obo_parser import GODag
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
import re
from collections import defaultdict
import chromadb
from chromadb.config import Settings

# ====== 1. 加载 BioBERT ======
MODEL_NAME = "dmis-lab/biobert-base-cased-v1.1"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

def encode_text(text: str):
    """返回文本的平均池化 embedding"""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
    with torch.no_grad():
        outputs = model(**inputs)
    last_hidden = outputs.last_hidden_state  # [batch, seq_len, hidden]
    embedding = last_hidden.mean(dim=1).squeeze().numpy()
    return embedding

def split_sentences(text: str):
    """将文本分割成句子"""
    # 使用多种分隔符分割句子
    sentences = re.split(r'[。！？；\n]+', text)
    # 过滤空句子和太短的句子
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    return sentences

# ====== 2. 初始化 ChromaDB ======
def init_chromadb():
    """初始化ChromaDB客户端和集合"""
    client = chromadb.Client(Settings())
    collection_name = "go_terms_embeddings"
    
    try:
        collection = client.get_collection(name=collection_name)
        print(f"已加载现有集合: {collection_name}")
        return collection
    except:
        print(f"创建新集合: {collection_name}")
        collection = client.create_collection(name=collection_name)
        return collection

# ====== 3. 解析 GO 本体 ======
import os

def load_cafa_go_terms(cafa_dir="Agents/CAFA"):
    """尝试加载CAFA提供的GO terms文件"""
    # 只检查go.txt文件
    go_file = os.path.join(cafa_dir, "go.txt")
    
    if os.path.exists(go_file):
        print(f"发现CAFA GO terms文件: {go_file}")
        return parse_cafa_go_file(go_file)
    
    print("未找到CAFA go.txt文件，使用go-basic.obo")
    return None

def parse_cafa_go_file(file_path):
    """解析CAFA的OBO格式GO terms文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("正在解析OBO格式文件...")
        return parse_obo_format(lines)
        
    except Exception as e:
        print(f"解析CAFA GO terms文件失败: {e}")
        return None

def parse_obo_format(lines):
    """解析OBO格式的GO terms文件"""
    go_terms = {}
    current_term = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line == '[Term]':
            # 开始新的term
            if current_term:
                # 保存前一个term
                go_terms[current_term['id']] = create_go_term_object(current_term)
            current_term = {'id': '', 'name': '', 'namespace': '', 'definition': ''}
        elif line.startswith('id: '):
            current_term['id'] = line[4:].strip()
        elif line.startswith('name: '):
            current_term['name'] = line[6:].strip()
        elif line.startswith('namespace: '):
            current_term['namespace'] = line[11:].strip()
        elif line.startswith('def: '):
            current_term['definition'] = line[5:].strip()
    
    # 保存最后一个term
    if current_term and current_term['id']:
        go_terms[current_term['id']] = create_go_term_object(current_term)
    
    print(f"成功解析 {len(go_terms)} 个OBO格式的CAFA GO terms")
    return go_terms



def create_go_term_object(term_data):
    """创建GO term对象"""
    class SimpleGOTerm:
        def __init__(self, go_id, name, namespace, definition=""):
            self.id = go_id
            self.name = name
            self.namespace = namespace
            self.definition = definition
            self.children = []  # 简化处理，不解析层次关系
    
    return SimpleGOTerm(
        term_data['id'], 
        term_data['name'], 
        term_data['namespace'], 
        term_data.get('definition', '')
    )

# 尝试加载CAFA GO terms，如果没有则使用go-basic.obo
cafa_go = load_cafa_go_terms()
if cafa_go:
    go = cafa_go
    print("使用CAFA提供的GO terms")
else:
    from goatools.base import download_go_basic_obo
    go = GODag(download_go_basic_obo())
    print("使用go-basic.obo")

# 筛选GO terms
def filter_go_terms(go_dict, min_freq=1, exclude_iea=False, max_terms_per_namespace=1000):
    """筛选GO terms，使用基于重要性和质量的筛选策略"""
    filtered_terms = {}
    namespace_counts = {'biological_process': 0, 'molecular_function': 0, 'cellular_component': 0}
    
    # 按namespace分组并计算优先级
    namespace_terms = {
        'biological_process': [],
        'molecular_function': [], 
        'cellular_component': []
    }
    
    for go_id, term in go_dict.items():
        # 1. 只保留BP, MF, CC三种类型
        if term.namespace not in ['biological_process', 'molecular_function', 'cellular_component']:
            continue
            
        # 2. 计算综合优先级分数
        priority_score = 0
        if hasattr(term, 'definition') and term.definition.strip():
            priority_score += 2  # 有definition的+2分
        
        # 3. 基于GO ID的层次深度进行筛选（浅层terms通常更重要）
        # GO:0000001 比 GO:0000001.0000001 更重要
        if '.' not in go_id:
            priority_score += 3  # 顶级terms +3分
        elif go_id.count('.') == 1:
            priority_score += 2  # 二级terms +2分
        elif go_id.count('.') == 2:
            priority_score += 1  # 三级terms +1分
        
        # 4. 基于名称长度（名称太长的可能过于具体）
        name_length = len(term.name)
        if name_length < 50:
            priority_score += 1  # 名称简洁的+1分
        
        namespace_terms[term.namespace].append((go_id, term, priority_score))
    
    # 对每个namespace，按优先级排序并选择前max_terms_per_namespace个terms
    for namespace, terms_list in namespace_terms.items():
        # 按优先级排序
        terms_list.sort(key=lambda x: x[2], reverse=True)
        # 选择前max_terms_per_namespace个terms
        selected_terms = terms_list[:max_terms_per_namespace]
        
        for go_id, term, _ in selected_terms:
            filtered_terms[go_id] = term
            namespace_counts[namespace] += 1
    
    print(f"筛选结果统计：")
    for namespace, count in namespace_counts.items():
        print(f"  {namespace}: {count} terms")
    
    return filtered_terms

# ====== 4. 构建和存储 GO terms embeddings ======
def build_go_embeddings(collection, filtered_go):
    """构建GO terms embeddings并存储到ChromaDB"""
    print("正在计算GO terms的embeddings...")
    
    # 检查是否已有数据
    try:
        count = collection.count()
        if count > 0:
            print(f"ChromaDB中已有 {count} 个GO terms embeddings")
            return
    except:
        pass
    
        # 构建embeddings
    documents = []
    embeddings = []
    ids = []
    metadatas = []
    
    count = 0
    for go_id, term in filtered_go.items():
        text = term.name
        if hasattr(term, 'definition') and term.definition:
            text += " " + term.definition
        
        try:
            embedding = encode_text(text)
            
            documents.append(text)
            embeddings.append(embedding.tolist())
            ids.append(go_id)
            metadatas.append({
                "name": term.name,
                "namespace": term.namespace,
                "definition": term.definition if hasattr(term, 'definition') else ""
            })
            
            count += 1
            if count % 100 == 0:
                print(f"已处理 {count}/{len(filtered_go)} 个GO terms...")
                
        except Exception as e:
            print(f"跳过 {go_id}: {e}")
            continue
    
    # 批量添加到ChromaDB
    if documents:
        collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
        print(f"成功存储 {len(documents)} 个GO terms embeddings到ChromaDB")

# ====== 5. 归一化函数 ======
def normalize_scores(scores_dict):
        min_score = min(scores_dict.values())
        max_score = max(scores_dict.values())
        if max_score == min_score:
            # 如果所有分数相同，给一个小的随机扰动
            import random
            return {go_id: 0.5 + random.uniform(-0.1, 0.1) for go_id in scores_dict.keys()}
        
        normalized = {}
        for go_id, score in scores_dict.items():
            norm_score = 0.1 + 0.8 * (score - min_score) / (max_score - min_score)
            normalized[go_id] = norm_score
        return normalized
    
   

# ====== 6. 使用ChromaDB预测GO terms ======
def predict_go_terms_chromadb(collection, description: str, top_k=5, balance_namespaces=True):
    """使用ChromaDB预测GO terms，支持平衡三大类覆盖"""
    # 分割句子
    sentences = split_sentences(description)
    print(f"分割得到 {len(sentences)} 个句子:")
    for i, sent in enumerate(sentences, 1):
        print(f"  {i}. {sent[:80]}...")
    print()
    
    # 对每个句子预测GO terms
    all_scores = defaultdict(list)
    
    for i, sentence in enumerate(sentences, 1):
        print(f"处理句子 {i}: {sentence[:60]}...")
        
        # 计算当前句子的embedding
        try:
            sent_emb = encode_text(sentence)
        except Exception as e:
            print(f"  跳过句子 {i} (编码失败): {e}")
            continue
        
        # 使用ChromaDB查询相似GO terms
        try:
            results = collection.query(
                query_embeddings=[sent_emb.tolist()],
                n_results=top_k * 3,  # 查询更多结果以便后续平衡
                include=["documents", "metadatas", "distances"]
            )
            
            # 检查查询结果
            if not results["ids"] or not results["ids"][0]:
                print(f"    警告：句子 {i} 没有找到匹配的GO terms")
                continue
                
            print(f"  句子 {i} 的top {len(results['ids'][0])} GO terms:")
            for j, (doc, metadata, distance) in enumerate(zip(
                results["documents"][0], 
                results["metadatas"][0], 
                results["distances"][0]
            )):
                go_id = results["ids"][0][j]
                # 距离转换为相似度：距离越小，相似度越高
                # 使用更温和的转换方式，避免距离过大时score为0
                score = 1 / (1 + distance/10)  # 除以10让距离范围更合理
                print(f"    {go_id}: {metadata['name']} (distance={distance:.3f}, score={score:.3f}) [{metadata['namespace']}]")
                all_scores[go_id].append(score)
        except Exception as e:
            print(f"    错误：句子 {i} 查询失败: {e}")
            continue
        print()
    
    # 汇总所有句子的结果
    final_scores = {}
    for go_id, scores in all_scores.items():
        # 使用最高分数作为最终分数
        final_scores[go_id] = max(scores)
    
    if balance_namespaces:
        # 平衡三大类覆盖
        balanced_results = balance_namespace_coverage(collection, final_scores, top_k)
        return balanced_results
    else:
        # 传统方式：直接取top_k
        print(f"\n所有候选GO terms分数范围: {min(final_scores.values()):.3f} - {max(final_scores.values()):.3f}")
        top_k_scores = dict(sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:top_k])
        
        # 对前 top_k 个进行归一化，使分布更合理
        print(f"前{top_k}个GO terms归一化前分数范围: {min(top_k_scores.values()):.3f} - {max(top_k_scores.values()):.3f}")
        normalized_scores = normalize_scores(top_k_scores)
        print(f"前{top_k}个GO terms归一化后分数范围: {min(normalized_scores.values()):.3f} - {max(normalized_scores.values()):.3f}")
        
        # 返回归一化后的结果（保持排序）
        ranked = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked

def balance_namespace_coverage(collection, final_scores, top_k):
    """平衡三大类GO terms的覆盖，使用namespace内部分数正则化"""
    # 获取每个GO term的namespace信息
    go_namespaces = {}
    for go_id in final_scores.keys():
        try:
            # 从collection中获取metadata
            results = collection.get(ids=[go_id], include=["metadatas"])
            if results["metadatas"]:
                go_namespaces[go_id] = results["metadatas"][0]["namespace"]
        except:
            continue
    
    # 按namespace分组
    namespace_scores = {
        'biological_process': [],
        'molecular_function': [],
        'cellular_component': []
    }
    
    for go_id, score in final_scores.items():
        namespace = go_namespaces.get(go_id, 'unknown')
        if namespace in namespace_scores:
            namespace_scores[namespace].append((go_id, score))
    
    # 对每个namespace内部进行分数正则化
    print("\n各namespace原始分数统计：")
    for namespace, terms_list in namespace_scores.items():
        if terms_list:
            scores = [score for _, score in terms_list]
            print(f"  {namespace}: {len(terms_list)} terms, 分数范围 {min(scores):.3f} - {max(scores):.3f}")
    
    # 在每个namespace内部进行正则化
    normalized_namespace_scores = {}
    for namespace, terms_list in namespace_scores.items():
        if not terms_list:
            continue
            
        # 提取分数
        scores = [score for _, score in terms_list]
        go_ids = [go_id for go_id, _ in terms_list]
        
        # 在namespace内部进行正则化
        normalized_scores = normalize_scores_within_namespace(scores)
        
        # 重新组合
        normalized_namespace_scores[namespace] = list(zip(go_ids, normalized_scores))
    
    print("\n各namespace正则化后分数统计：")
    for namespace, terms_list in normalized_namespace_scores.items():
        if terms_list:
            scores = [score for _, score in terms_list]
            print(f"  {namespace}: {len(terms_list)} terms, 分数范围 {min(scores):.3f} - {max(scores):.3f}")
    
    # 对每个namespace按正则化后的分数排序
    for namespace in normalized_namespace_scores:
        normalized_namespace_scores[namespace].sort(key=lambda x: x[1], reverse=True)
    
    # 平衡选择：每个namespace选择一定数量的terms
    balanced_terms = {}
    terms_per_namespace = max(1, top_k // 3)  # 每个namespace至少1个，平均分配
    
    for namespace, terms_list in normalized_namespace_scores.items():
        selected_terms = terms_list[:terms_per_namespace]
        for go_id, score in selected_terms:
            balanced_terms[go_id] = score
    
    # 如果还不够top_k个，从剩余的高分terms中补充
    remaining_slots = top_k - len(balanced_terms)
    if remaining_slots > 0:
        # 收集所有未选中的terms
        remaining_terms = []
        for namespace, terms_list in normalized_namespace_scores.items():
            for go_id, score in terms_list[terms_per_namespace:]:
                remaining_terms.append((go_id, score))
        
        # 按正则化后的分数排序，选择最高的
        remaining_terms.sort(key=lambda x: x[1], reverse=True)
        for go_id, score in remaining_terms[:remaining_slots]:
            balanced_terms[go_id] = score
    
    # 最终归一化（可选，用于调整最终分数范围）
    if balanced_terms:
        print(f"\n平衡后的GO terms分数范围: {min(balanced_terms.values()):.3f} - {max(balanced_terms.values()):.3f}")
        final_normalized_scores = normalize_scores(balanced_terms)
        print(f"最终归一化后分数范围: {min(final_normalized_scores.values()):.3f} - {max(final_normalized_scores.values()):.3f}")
        
        # 返回排序结果
        ranked = sorted(final_normalized_scores.items(), key=lambda x: x[1], reverse=True)
        return ranked
    else:
        print("警告：没有找到任何GO terms，返回空结果")
        return []

def normalize_scores_within_namespace(scores):
    """在单个namespace内部进行分数正则化"""
    if not scores:
        return []
    
    min_score = min(scores)
    max_score = max(scores)
    
    if max_score == min_score:
        # 如果所有分数相同，给一个小的随机扰动
        import random
        return [0.5 + random.uniform(-0.1, 0.1) for _ in scores]
    
    # 使用Min-Max归一化到[0.1, 0.9]范围
    normalized = []
    for score in scores:
        norm_score = 0.1 + 0.8 * (score - min_score) / (max_score - min_score)
        normalized.append(norm_score)
    
    return normalized

# ====== 7. 读取多智能体分析结果 ======
def read_multi_agent_result(result_file="Agents/CAFA/analysis_result_with_confidence.txt"):
    """读取多智能体系统的综合分析结果"""
    if not os.path.exists(result_file):
        print(f"错误：找不到结果文件 {result_file}")
        return None
    
    with open(result_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 提取综合分析部分
    if "COMPREHENSIVE ANALYSIS" in content:
        # 找到综合分析部分
        start_idx = content.find("COMPREHENSIVE ANALYSIS")
        if start_idx != -1:
            # 从综合分析开始到下一个部分或文件结束
            comprehensive_part = content[start_idx:]
            
            # 查找下一个部分的开始（如CONFIDENCE SUMMARY）
            next_section_markers = ["CONFIDENCE SUMMARY", "📊 CONFIDENCE SUMMARY"]
            end_idx = len(comprehensive_part)
            for marker in next_section_markers:
                marker_idx = comprehensive_part.find(marker)
                if marker_idx != -1 and marker_idx < end_idx:
                    end_idx = marker_idx
            
            # 提取综合分析部分
            comprehensive_text = comprehensive_part[:end_idx]
            
            # 提取置信度行之后的内容
            lines = comprehensive_text.split('\n')
            result_lines = []
            found_content = False
            for line in lines:
                if "Confidence:" in line and "[" in line:
                    found_content = True
                    continue
                if found_content and line.strip():
                    result_lines.append(line)
            
            if result_lines:
                return '\n'.join(result_lines)
    
    print("警告：未找到综合分析结果，尝试读取整个文件内容")
    return content

# ====== 8. 主函数 ======
def main():
    # 初始化ChromaDB
    collection = init_chromadb()
    
    # 检查ChromaDB状态
    try:
        count = collection.count()
        print(f"ChromaDB集合中共有 {count} 个GO terms")
        if count == 0:
            print("警告：ChromaDB为空，需要重新构建embeddings")
    except Exception as e:
        print(f"ChromaDB状态检查失败: {e}")
    
    # 筛选GO terms，使用基于重要性的筛选策略
    print("正在筛选GO terms...")
    filtered_go = filter_go_terms(go, min_freq=1, exclude_iea=False, max_terms_per_namespace=1000)
    print(f"筛选后剩余 {len(filtered_go)} 个GO terms")
    
    # 构建embeddings（如果还没有的话）
    build_go_embeddings(collection, filtered_go)
    
    # 再次检查ChromaDB状态
    try:
        final_count = collection.count()
        print(f"构建完成后，ChromaDB中共有 {final_count} 个GO terms")
    except Exception as e:
        print(f"最终ChromaDB状态检查失败: {e}")
    
    # 读取多智能体分析结果
    description = read_multi_agent_result()
    if not description:
        print("无法读取分析结果，使用示例描述")
        description = "This protein is involved in ATP binding and located in the nucleus."
    
    print("=" * 60)
    print("多智能体系统综合分析结果：")
    print("=" * 60)
    print(description)
    print("=" * 60)
    
    # 预测GO terms
    print("\n预测的GO terms（平衡三大类覆盖）：")
    print("-" * 60)
    preds = predict_go_terms_chromadb(collection, description, top_k=20, balance_namespaces=True)
    
    # 统计namespace分布
    namespace_stats = {'biological_process': 0, 'molecular_function': 0, 'cellular_component': 0}
    
    for i, (go_id, score) in enumerate(preds, 1):
        term = go[go_id]
        namespace = term.namespace
        namespace_stats[namespace] = namespace_stats.get(namespace, 0) + 1
        
        print(f"{i:2d}. {go_id:12s} | {term.name:50s} | score={score:.3f} | [{namespace}]")
        if hasattr(term, 'definition') and term.definition:
            print(f"     {term.definition[:80]}...")
        print()
    
    print("Namespace分布统计：")
    for namespace, count in namespace_stats.items():
        print(f"  {namespace}: {count} terms")

if __name__ == "__main__":
    main()
