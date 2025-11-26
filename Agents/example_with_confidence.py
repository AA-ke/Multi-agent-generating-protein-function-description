"""
多智能体蛋白质分析系统 - 带置信度的使用示例
"""

from update import app, format_output_with_confidence

def analyze_protein_with_confidence(sequence: str):
    """
    分析蛋白质序列并显示置信度
    
    Args:
        sequence: 蛋白质序列字符串
    """
    print("🚀 Starting protein analysis with confidence scoring...")
    print(f"Input sequence: {sequence[:50]}...")
    print()
    
    try:
        # 运行分析
        result = app.invoke({"input": sequence})
        
        # 格式化并显示结果
        formatted_result = format_output_with_confidence(result)
        print(formatted_result)
        
        # 返回置信度信息
        confidence_summary = {
            "sequence_confidence": result.get("sequence_confidence", 0.0),
            "structure_confidence": result.get("structure_confidence", 0.0),
            "final_confidence": result.get("final_confidence", 0.0)
        }
        
        return result, confidence_summary
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def print_confidence_summary(confidence_summary):
    """
    打印置信度总结
    """
    if confidence_summary:
        print("📊 CONFIDENCE SUMMARY")
        print("=" * 40)
        print(f"Sequence Analysis: {confidence_summary['sequence_confidence']:.1%}")
        print(f"Structure Analysis: {confidence_summary['structure_confidence']:.1%}")
        print(f"Final Analysis: {confidence_summary['final_confidence']:.1%}")
        
        # 计算平均置信度
        avg_confidence = sum(confidence_summary.values()) / len(confidence_summary)
        print(f"Average Confidence: {avg_confidence:.1%}")
        
        # 置信度评级
        if avg_confidence >= 0.8:
            rating = "🟢 HIGH"
        elif avg_confidence >= 0.6:
            rating = "🟡 MEDIUM"
        else:
            rating = "🔴 LOW"
        print(f"Overall Rating: {rating}")

if __name__ == "__main__":
    # 示例蛋白质序列
    test_sequences = [
        # 抗体片段
        "MASGQGPGPPRQECGEPALPSASEEQVAQDTEEVFRSYVFYRHQQEQEAEGVAAPADPEMVTLPLQPSSTMGQVGRQLAIIGDDINRRYDSEFQTMLQHLQPTAENAYEYFTKIATSLFESGINWGRVVALLGFGYRLALHVYQHGLTGFLGQVTRFVVDFMLHHCIARWIAQRGGWVAALNLGNGPILNVLVVLGVVLLGQFVVRRFFKS",
        
        # 胰岛素
        "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKT",
        
        # 肌红蛋白
        "MGLSDGEWQLVLNVWGKVEADIPGHGQEVLIRLFKGHPETLEKFDKFKHLKTEAEMKASEDLKKHGTVVLTALGGILKKKGHHEAELKPLAQSHATKHKIPIKYLEFISDAIIHVLHSKHPGDFGADAQGAMNKALELFRKDMASNYKELGFQG"
    ]
    
    print("🧬 Multi-Agent Protein Analysis System with Confidence Scoring")
    print("=" * 70)
    
    for i, seq in enumerate(test_sequences, 1):
        print(f"\n📋 Analysis {i}: {seq[:30]}...")
        print("-" * 50)
        
        try:
            result, confidence_summary = analyze_protein_with_confidence(seq)
            
            if result:
                print_confidence_summary(confidence_summary)
                print(f"✅ Analysis {i} completed successfully!")
                
                # 保存结果到文件
                filename = f"analysis_result_{i}_with_confidence.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(format_output_with_confidence(result))
                print(f"📄 Results saved to '{filename}'")
            else:
                print(f"❌ Analysis {i} failed!")
                
        except Exception as e:
            print(f"❌ Analysis {i} failed: {e}")
        
        print("=" * 70) 