
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()
google_client = genai.Client()

def calculate_reasoning_confidence(function_confidence, sequence_confidence, structure_confidence, function_nl, sequence_nl, structure_nl) -> float:
    """
    计算推理分析的置信度
    
    Args:
        function_confidence: 功能分析置信度
        sequence_confidence: 序列分析置信度
        structure_confidence: 结构分析置信度
        function_nl: 功能分析结果
        sequence_nl: 序列分析结果
        structure_nl: 结构分析结果
    
    Returns:
        综合置信度分数 (0-1)
    """
    try:
        # 1. 基于子agent置信度的加权平均 - 功能智能体权重最高
        sub_agent_confidence = (function_confidence * 0.5 + sequence_confidence * 0.3 + structure_confidence * 0.2)
        
        # 2. 基于分析结果一致性的置信度
        # 检查三个分析结果是否都包含关键信息
        function_has_info = len(function_nl) > 100
        sequence_has_info = len(sequence_nl) > 100
        structure_has_info = len(structure_nl) > 100
        
        info_count = sum([function_has_info, sequence_has_info, structure_has_info])
        if info_count == 3:
            consistency_confidence = 1.0
        elif info_count == 2:
            consistency_confidence = 0.8
        elif info_count == 1:
            consistency_confidence = 0.6
        else:
            consistency_confidence = 0.4
        
        # 3. 基于分析结果详细程度的置信度
        detail_confidence = min(1.0, (len(function_nl) + len(sequence_nl) + len(structure_nl)) / 1500)
        
        # 综合置信度 - 功能智能体影响最大
        confidence = (sub_agent_confidence * 0.6 + 
                     consistency_confidence * 0.3 + 
                     detail_confidence * 0.1)
        
        return min(1.0, max(0.0, confidence))
        
    except Exception as e:
        print(f"Warning: Error calculating reasoning confidence: {e}")
        return 0.5  # 默认中等置信度

def reasoning_agent(state: dict) -> dict:
    """
    综合三个agent的分析结果，生成最终结论
    
    Args:
        state: 包含function_nl、sequence_nl、structure_nl和置信度的字典
    
    Returns:
        包含final_answer和final_confidence的字典
    """
    seq = state["input"]
    function_nl = state.get("function_nl", "")
    sequence_nl = state.get("sequence_nl", "")
    structure_nl = state.get("structure_nl", "")
    function_confidence = state.get("function_confidence", 0.5)
    sequence_confidence = state.get("sequence_confidence", 0.5)
    structure_confidence = state.get("structure_confidence", 0.5)
    
    prompt = f"""You are a protein function summary expert. Please synthesize the analysis from function expert, sequence expert, and structure expert to summarize the potential functions, pathways, domains, and disease associations of this protein.

Function expert analysis (confidence: {function_confidence:.2f}):
{function_nl}

Sequence expert analysis (confidence: {sequence_confidence:.2f}):
{sequence_nl}

Structure expert analysis (confidence: {structure_confidence:.2f}):
{structure_nl}

Notes:
1. The function expert analysis is based on GO terms prediction and has higher authority, so it should be given more weight
2. If a certain expert has low confidence, please adjust the reliance on that expert's analysis accordingly
3. Please highlight the consistency and complementarity among the expert analysis results

Please synthesize the above three expert analyses and generate a comprehensive, accurate, and fluent natural language functional description from three aspects:
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
    
    # 计算综合置信度
    final_confidence = calculate_reasoning_confidence(
        function_confidence,
        sequence_confidence, 
        structure_confidence, 
        function_nl,
        sequence_nl, 
        structure_nl
    )
    
    return {
        "final_answer": response.text,
        "final_confidence": final_confidence
    }