import requests
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()
google_client = genai.Client()

def get_go_terms(sequence, threshold=0.3):
    """
    调用 DeepGO API 获取蛋白质的 GO terms
    
    Args:
        sequence: 蛋白质序列
        threshold: 置信度阈值
    
    Returns:
        GO terms 结果
    """
    url = "https://deepgo.cbrc.kaust.edu.sa/deepgo/api/create"
    headers = {"Content-Type": "application/json"}

    payload = {
        "version": "latest",
        "data_format": "fasta",
        "data": sequence,
        "threshold": threshold
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"DeepGO API 请求失败: {e}")
        return None

def parse_go_terms(go_response):
    """
    解析 GO terms 响应，提取关键信息
    
    Args:
        go_response: DeepGO API 响应
    
    Returns:
        格式化的 GO terms 信息
    """
    if not go_response:
        return "无法获取 GO terms 信息"
    
    # 直接返回原始响应，让 LLM 处理
    return json.dumps(go_response, indent=2, ensure_ascii=False)

def calculate_function_confidence(go_response, sequence) -> float:
    """
    计算功能分析的置信度
    根据用户要求，功能智能体的置信度应该最高
    
    Args:
        go_response: DeepGO API 响应
        sequence: 蛋白质序列
    
    Returns:
        置信度分数 (0-1)
    """
    if not go_response:
        return 0.3
    
    # 功能智能体应该有最高置信度
    return 0.8

def generate_function_description(sequence, go_terms_text) -> str:
    """
    使用 LLM 根据 GO terms 生成功能描述
    
    Args:
        sequence: 蛋白质序列
        go_terms_text: 格式化的 GO terms 信息
    
    Returns:
        功能描述文本
    """
    prompt = f"""
    You are a protein function prediction expert. Please provide a detailed functional analysis based on the following protein sequence and GO terms prediction results:

    Protein sequence:
    {sequence}

    GO Terms prediction results:
    {go_terms_text}

    Please provide a comprehensive functional analysis from three aspects:
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

def function_agent(state: dict) -> dict:
    """
    功能智能体主函数
    
    Args:
        state: 包含 input (序列) 的状态字典
    
    Returns:
        包含 function_nl 和 function_confidence 的字典
    """
    sequence = state["input"]
    
    # 获取 GO terms
    go_response = get_go_terms(sequence, threshold=0.3)
    
    # 解析 GO terms
    go_terms_text = parse_go_terms(go_response)
    
    # 生成功能描述
    function_nl = generate_function_description(sequence, go_terms_text)
    
    # 计算置信度
    function_confidence = calculate_function_confidence(go_response, sequence)
    
    return {
        "function_nl": function_nl,
        "function_confidence": function_confidence
    }
