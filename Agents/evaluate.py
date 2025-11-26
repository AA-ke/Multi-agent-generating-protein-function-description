import json
import re
from typing import Dict, List
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# 下载必要的NLTK数据
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class TextSimilarityEvaluator:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        # 可选组件状态
        self._bert_score_available = None
        
    def preprocess_text(self, text: str) -> str:
        """预处理文本：小写化、去除标点、词干化"""
        if not text:
            return ""
        
        # 转换为小写
        text = text.lower()
        
        # 去除特殊字符和数字，保留字母和空格
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # 分词
        tokens = word_tokenize(text)
        
        # 去除停用词和词干化
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words and len(token) > 2:
                lemmatized = self.lemmatizer.lemmatize(token)
                processed_tokens.append(lemmatized)
        
        return ' '.join(processed_tokens)

    def calculate_bm25_similarity(self, reference: str, candidate: str, k1: float = 1.5, b: float = 0.75) -> float:
        """计算 BM25 相似度（参考作为查询，候选作为文档），返回0-1归一化分数"""
        if not reference or not candidate:
            return 0.0
        # 语料：参考与候选两篇文档，用于估计IDF
        ref_tokens = self.preprocess_text(reference).split()
        cand_tokens = self.preprocess_text(candidate).split()
        if not ref_tokens or not cand_tokens:
            return 0.0
        corpus = [ref_tokens, cand_tokens]
        N = 2
        dl = len(cand_tokens)
        avgdl = (len(ref_tokens) + len(cand_tokens)) / 2
        # 词频与文档频
        from collections import Counter
        tf_doc = Counter(cand_tokens)
        df = {}
        for token in set(ref_tokens):
            df[token] = sum(1 for doc in corpus if token in doc)
        # BM25 打分（对参考中的唯一词求和）
        score = 0.0
        unique_query_terms = set(ref_tokens)
        for term in unique_query_terms:
            n_q = df.get(term, 0)
            # 加1防止负值和极端
            idf = np.log((N - n_q + 0.5) / (n_q + 0.5) + 1.0)
            f = tf_doc.get(term, 0)
            denom = f + k1 * (1 - b + b * dl / avgdl)
            if denom == 0:
                continue
            term_score = idf * (f * (k1 + 1)) / denom
            score += term_score
        # 简单归一化到0-1（可按需调整常数）
        norm_score = score / (score + 10.0)
        return float(max(0.0, min(1.0, norm_score)))

    def _ensure_bert_score(self):
        """懒检查 bert_score 是否可用。"""
        if self._bert_score_available is not None:
            return self._bert_score_available
        try:
            import bert_score  # noqa: F401
            self._bert_score_available = True
        except Exception as e:
            print(f"Warning: bert_score not available ({e}), BERTScore will be 0.0")
            self._bert_score_available = False
        return self._bert_score_available

    def calculate_bertscore_f1(self, reference: str, candidate: str, lang: str = "en") -> float:
        """计算 BERTScore F1，相似度范围 [0,1]。依赖不可用时返回 0。"""
        if not reference or not candidate:
            return 0.0
        if not self._ensure_bert_score():
            return 0.0
        try:
            from bert_score import score as bert_score_fn
            P, R, F1 = bert_score_fn([candidate], [reference], lang=lang, verbose=False)
            f1 = float(F1.mean().item())
            return max(0.0, min(1.0, f1))
        except Exception as e:
            print(f"Warning: BERTScore failed: {e}")
            return 0.0
    
    def calculate_jaccard_similarity(self, text1: str, text2: str) -> float:
        """计算Jaccard相似度"""
        if not text1 or not text2:
            return 0.0
        
        # 预处理文本
        processed1 = set(self.preprocess_text(text1).split())
        processed2 = set(self.preprocess_text(text2).split())
        
        if not processed1 and not processed2:
            return 1.0
        if not processed1 or not processed2:
            return 0.0
        
        intersection = len(processed1.intersection(processed2))
        union = len(processed1.union(processed2))
        
        return intersection / union if union > 0 else 0.0
    
    def calculate_bleu_score(self, reference: str, candidate: str) -> float:
        """简化的BLEU分数计算（基于n-gram重叠）"""
        if not reference or not candidate:
            return 0.0
        
        ref_tokens = self.preprocess_text(reference).split()
        cand_tokens = self.preprocess_text(candidate).split()
        
        if not ref_tokens or not cand_tokens:
            return 0.0
        
        # 计算1-gram和2-gram的精确度
        def get_ngrams(tokens, n):
            return [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]
        
        # 1-gram精确度
        ref_1gram = set(get_ngrams(ref_tokens, 1))
        cand_1gram = set(get_ngrams(cand_tokens, 1))
        p1 = len(ref_1gram.intersection(cand_1gram)) / len(cand_1gram) if cand_1gram else 0
        
        # 2-gram精确度
        ref_2gram = set(get_ngrams(ref_tokens, 2))
        cand_2gram = set(get_ngrams(cand_tokens, 2))
        p2 = len(ref_2gram.intersection(cand_2gram)) / len(cand_2gram) if cand_2gram else 0
        
        # 简化的BLEU分数
        bleu = (p1 * p2) ** 0.5
        return bleu
    
    def extract_agent_results(self, analysis_text: str) -> Dict[str, str]:
        """从分析结果中提取各个agent的输出"""
        results = {}
        
        # 提取Function Agent结果
        func_match = re.search(r'🎯 FUNCTION ANALYSIS.*?----------------------------------------\n(.*?)(?=\n🔬|\n🧬|\n🎯|\n📊|\Z)', analysis_text, re.DOTALL)
        if func_match:
            results['function_agent'] = func_match.group(1).strip()
        
        # 提取Sequence Agent结果
        seq_match = re.search(r'🔬 SEQUENCE ANALYSIS.*?----------------------------------------\n(.*?)(?=\n🧬|\n🎯|\n📊|\Z)', analysis_text, re.DOTALL)
        if seq_match:
            results['sequence_agent'] = seq_match.group(1).strip()
        
        # 提取Structure Agent结果
        struct_match = re.search(r'🧬 STRUCTURE ANALYSIS.*?----------------------------------------\n(.*?)(?=\n🎯|\n📊|\Z)', analysis_text, re.DOTALL)
        if struct_match:
            results['structure_agent'] = struct_match.group(1).strip()
        
        # 提取Comprehensive Analysis结果
        comp_match = re.search(r'🎯 COMPREHENSIVE ANALYSIS.*?----------------------------------------\n(.*?)(?=\n📊|\Z)', analysis_text, re.DOTALL)
        if comp_match:
            results['comprehensive_analysis'] = comp_match.group(1).strip()
        
        return results
    
    def evaluate_all_similarities(self, standard_answer: str, analysis_result: str) -> Dict[str, Dict[str, float]]:
        """计算所有相似度指标"""
        # 提取各个agent的结果
        agent_results = self.extract_agent_results(analysis_result)
        
        # 准备所有文本
        all_texts = [standard_answer]
        agent_names = []
        
        for agent_name, agent_text in agent_results.items():
            all_texts.append(agent_text)
            agent_names.append(agent_name)
        
        # 计算各种相似度指标
        similarities = {}
        
        for i, agent_name in enumerate(agent_names):
            agent_text = agent_results[agent_name]
            
            # Jaccard相似度
            jaccard_sim = self.calculate_jaccard_similarity(standard_answer, agent_text)
            
            # BLEU分数
            bleu_score = self.calculate_bleu_score(standard_answer, agent_text)
            
            # BM25 相似度（参考为标准答案，候选为智能体输出）
            bm25_sim = self.calculate_bm25_similarity(standard_answer, agent_text)
            
            # BERTScore F1（英语）
            bert_f1 = self.calculate_bertscore_f1(standard_answer, agent_text, lang="en")

            similarities[agent_name] = {
                'jaccard': jaccard_sim,
                'bleu': bleu_score,
                'bm25': bm25_sim,
                'bertscore_f1': bert_f1,
                'average': (jaccard_sim + bleu_score + bm25_sim)*0.4 + 0.6*bert_f1
            }
        
        return similarities

def load_standard_answer(file_path: str) -> str:
    """加载标准答案"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        # 如果是JSON格式，提取文本内容
        if content.startswith('"') and content.endswith('"'):
            content = content[1:-1]  # 移除引号
            content = content.replace('\\n', '\n')  # 还原换行符
        return content

def load_analysis_result(file_path: str) -> str:
    """加载分析结果"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def print_evaluation_results(similarities: Dict[str, Dict[str, float]]):
    """打印评估结果"""
    print("=" * 80)
    print("多智能体系统评估结果")
    print("=" * 80)
    
    # 按平均相似度排序
    sorted_agents = sorted(similarities.items(), key=lambda x: x[1]['average'], reverse=True)
    
    print(f"{'智能体':<20} {'Jaccard':<10} {'BLEU':<10} {'BM25':<10} {'BERTScore':<10} {'平均分':<10} {'排名':<5}")
    print("-" * 80)
    
    for rank, (agent_name, scores) in enumerate(sorted_agents, 1):
        print(f"{agent_name:<20} {scores['jaccard']:<10.3f} "
              f"{scores['bleu']:<10.3f} {scores['bm25']:<10.3f} {scores['bertscore_f1']:<10.3f} {scores['average']:<10.3f} {rank:<5}")
    
    print("\n" + "=" * 80)
    print("详细分析:")
    print("=" * 80)
    
    for agent_name, scores in sorted_agents:
        print(f"\n{agent_name.upper()}:")
        print(f"  Jaccard相似度: {scores['jaccard']:.3f}")
        print(f"  BLEU分数: {scores['bleu']:.3f}")
        print(f"  BM25相似度: {scores['bm25']:.3f}")
        print(f"  BERTScore(F1): {scores['bertscore_f1']:.3f}")
        print(f"  综合平均分: {scores['average']:.3f}")
        
        

def save_evaluation_results(similarities: Dict[str, Dict[str, float]], output_file: str):
    """保存评估结果到JSON文件"""
    results = {
        'evaluation_metrics': similarities,
        'summary': {
            'best_agent': max(similarities.items(), key=lambda x: x[1]['average'])[0],
            'worst_agent': min(similarities.items(), key=lambda x: x[1]['average'])[0],
            'overall_average': np.mean([scores['average'] for scores in similarities.values()])
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n评估结果已保存到: {output_file}")

def main():
    """主函数"""
    # 初始化评估器
    evaluator = TextSimilarityEvaluator()
    
    # 加载数据
    print("加载标准答案和分析结果...")
    standard_answer = load_standard_answer("Agents/standard_answer_A0A087X1C5.txt")
    analysis_result = load_analysis_result("Agents/CAFA/analysis_result_with_confidence_A0A087X1C5.txt")
    
    print(f"标准答案长度: {len(standard_answer)} 字符")
    print(f"分析结果长度: {len(analysis_result)} 字符")
    
    # 计算相似度
    print("\n计算相似度指标...")
    similarities = evaluator.evaluate_all_similarities(standard_answer, analysis_result)
    
    # 打印结果
    print_evaluation_results(similarities)
    
    # 保存结果
    save_evaluation_results(similarities, "Agents/evaluation_results_A0A087X1C5.json")
    
    return similarities

if __name__ == "__main__":
    results = main()
