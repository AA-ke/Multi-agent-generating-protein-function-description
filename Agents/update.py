from langgraph.graph import StateGraph, END
from typing import TypedDict
from Seq_Agent import sequence_agent
from Struct_Agent import structure_agent
from Fuc_Agent import function_agent
from Reasoning_Agent import reasoning_agent

class AgentState(TypedDict):
    input: str
    sequence_nl: str
    structure_nl: str
    function_nl: str
    sequence_confidence: float
    structure_confidence: float
    function_confidence: float
    final_answer: str
    final_confidence: float

def format_output_with_confidence(result: dict) -> str:
    """
    格式化输出结果，包含置信度信息
    """
    output = "\n" + "=" * 60 + "\n"
    output += "MULTI-AGENT PROTEIN ANALYSIS RESULTS\n"
    output += "=" * 60 + "\n\n"
    
    # Function Agent结果 (最高优先级)
    if 'function_nl' in result:
        confidence = result.get('function_confidence', 0.0)
        confidence_bar = "█" * int(confidence * 10) + "░" * (10 - int(confidence * 10))
        output += f"🎯 FUNCTION ANALYSIS (Confidence: {confidence:.2f})\n"
        output += f"Confidence: [{confidence_bar}] {confidence:.1%}\n"
        output += "-" * 40 + "\n"
        output += result['function_nl'] + "\n\n"
    
    # Sequence Agent结果
    if 'sequence_nl' in result:
        confidence = result.get('sequence_confidence', 0.0)
        confidence_bar = "█" * int(confidence * 10) + "░" * (10 - int(confidence * 10))
        output += f"🔬 SEQUENCE ANALYSIS (Confidence: {confidence:.2f})\n"
        output += f"Confidence: [{confidence_bar}] {confidence:.1%}\n"
        output += "-" * 40 + "\n"
        output += result['sequence_nl'] + "\n\n"
    
    # Structure Agent结果
    if 'structure_nl' in result:
        confidence = result.get('structure_confidence', 0.0)
        confidence_bar = "█" * int(confidence * 10) + "░" * (10 - int(confidence * 10))
        output += f"🧬 STRUCTURE ANALYSIS (Confidence: {confidence:.2f})\n"
        output += f"Confidence: [{confidence_bar}] {confidence:.1%}\n"
        output += "-" * 40 + "\n"
        output += result['structure_nl'] + "\n\n"
    
    # 综合分析结果
    if 'final_answer' in result:
        confidence = result.get('final_confidence', 0.0)
        confidence_bar = "█" * int(confidence * 10) + "░" * (10 - int(confidence * 10))
        output += f"🎯 COMPREHENSIVE ANALYSIS (Confidence: {confidence:.2f})\n"
        output += f"Confidence: [{confidence_bar}] {confidence:.1%}\n"
        output += "-" * 40 + "\n"
        output += result['final_answer'] + "\n\n"
    
    # 置信度总结
    output += "📊 CONFIDENCE SUMMARY\n"
    output += "-" * 40 + "\n"
    if 'function_confidence' in result:
        output += f"Function Analysis: {result['function_confidence']:.1%}\n"
    if 'sequence_confidence' in result:
        output += f"Sequence Analysis: {result['sequence_confidence']:.1%}\n"
    if 'structure_confidence' in result:
        output += f"Structure Analysis: {result['structure_confidence']:.1%}\n"
    if 'final_confidence' in result:
        output += f"Final Analysis: {result['final_confidence']:.1%}\n"
    
    return output

if __name__ == "__main__":
    graph = StateGraph(AgentState)
    graph.add_node("function", function_agent)
    graph.add_node("sequence", sequence_agent)
    graph.add_node("structure", structure_agent)
    graph.add_node("reasoning", reasoning_agent)

    # 并行入口 - 三个智能体并行运行
    graph.set_entry_point("function")
    graph.set_entry_point("sequence")
    graph.set_entry_point("structure")
    # 三个agent都完成后，进入reasoning
    graph.add_edge("function", "reasoning")
    graph.add_edge("sequence", "reasoning")
    graph.add_edge("structure", "reasoning")
    graph.add_edge("reasoning", END)

    app = graph.compile()
    
    # 测试序列
    test_sequence = "MGLEALVPLAMIVAIFLLLVDLMHRHQRWAARYPPGPLPLPGLGNLLHVDFQNTPYCFDQLRRRFGDVFSLQLAWTPVVVLNGLAAVREAMVTRGEDTADRPPAPIYQVLGFGPRSQGVILSRYGPAWREQRRFSVSTLRNLGLGKKSLEQWVTEEAACLCAAFADQAGRPFRPNGLLDKAVSNVIASLTCGRRFEYDDPRFLRLLDLAQEGLKEESGFLREVLNAVPVLPHIPALAGKVLRFQKAFLTQLDELLTEHRMTWDPAQPPRDLTEAFLAKKEKAKGSPESSFNDENLRIVVGNLFLAGMVTTSTTLAWGLLLMILHLDVQRGRRVSPGCPIVGTHVCPVRVQQEIDDVIGQVRRPEMGDQAHMPCTTAVIHEVQHFGDIVPLGVTHMTSRDIEVQGFRIPKGTTLITNLSSVLKDEAVWKKPFRFHPEHFLDAQGHFVKPEAFLPFSAGRRACLGEPLARMELFLFFTSLLQHFSFSVAAGQPRPSHSRVVSFLVTPSPYELCAVPR"
    
    print("🚀 Starting multi-agent protein analysis with confidence scoring...")
    print(f"Input sequence: {test_sequence[:50]}...")
    print()
    
    try:
        result = app.invoke({"input": test_sequence})
        
        # 格式化并显示结果
        formatted_output = format_output_with_confidence(result)
        print(formatted_output)
        
        # 保存结果到文件
        with open("Agents/CAFA/analysis_result_with_confidence_A0A087X1C5.txt", "w", encoding="utf-8") as f:
            f.write(formatted_output)
        print("✅ Analysis completed! Results saved to 'analysis_result_with_confidence_A0A087X1C5.txt'")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()