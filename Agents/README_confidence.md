# 多智能体蛋白质分析系统 - 置信度功能

## 概述

这个系统现在包含了置信度评分功能，可以为每个分析步骤提供可靠性评估。

## 置信度计算原理

### 1. Sequence Agent 置信度
- **距离置信度 (40%)**: 基于检索到的相似蛋白质的距离
- **结果数量置信度 (20%)**: 基于检索到的结果数量
- **序列长度置信度 (20%)**: 基于输入序列的长度
- **文档质量置信度 (20%)**: 基于检索到的文档内容丰富程度

### 2. Structure Agent 置信度
- **pLDDT置信度 (40%)**: 基于结构预测的pLDDT分数
- **结构完整性置信度 (20%)**: 基于蛋白质的残基数量
- **二级结构信息置信度 (20%)**: 基于是否成功获取二级结构信息
- **金属结合位点置信度 (10%)**: 基于是否检测到金属结合位点
- **分子大小置信度 (10%)**: 基于蛋白质的大小

### 3. Reasoning Agent 置信度
- **子agent置信度 (60%)**: 基于sequence和structure agent的置信度加权平均
- **一致性置信度 (30%)**: 基于两个子agent分析结果的一致性
- **详细程度置信度 (10%)**: 基于分析结果的详细程度

## 使用方法

### 基本使用

```python
from update import app, format_output_with_confidence

# 运行分析
result = app.invoke({"input": "YOUR_PROTEIN_SEQUENCE"})

# 格式化输出
formatted_output = format_output_with_confidence(result)
print(formatted_output)
```

### 完整示例

```python
from example_with_confidence import analyze_protein_with_confidence

# 分析蛋白质
result, confidence_summary = analyze_protein_with_confidence("YOUR_SEQUENCE")

# 查看置信度总结
print(f"Sequence Confidence: {confidence_summary['sequence_confidence']:.1%}")
print(f"Structure Confidence: {confidence_summary['structure_confidence']:.1%}")
print(f"Final Confidence: {confidence_summary['final_confidence']:.1%}")
```

## 输出格式

系统会生成包含置信度信息的格式化输出：

```
============================================================
MULTI-AGENT PROTEIN ANALYSIS RESULTS
============================================================

🔬 SEQUENCE ANALYSIS (Confidence: 0.85)
Confidence: [████████░░] 85.0%
----------------------------------------
[序列分析结果]

🧬 STRUCTURE ANALYSIS (Confidence: 0.72)
Confidence: [███████░░░] 72.0%
----------------------------------------
[结构分析结果]

🎯 COMPREHENSIVE ANALYSIS (Confidence: 0.78)
Confidence: [████████░░] 78.0%
----------------------------------------
[综合分析结果]

📊 CONFIDENCE SUMMARY
----------------------------------------
Sequence Analysis: 85.0%
Structure Analysis: 72.0%
Final Analysis: 78.0%
```

## 置信度评级

- 🟢 **HIGH** (≥80%): 高置信度，结果可靠
- 🟡 **MEDIUM** (60-79%): 中等置信度，结果基本可靠
- 🔴 **LOW** (<60%): 低置信度，需要谨慎对待结果

## 文件说明

- `update.py`: 主程序，包含置信度功能
- `example_with_confidence.py`: 使用示例
- `Seq_Agent.py`: 序列分析agent，包含置信度计算
- `Struct_Agent.py`: 结构分析agent，包含置信度计算
- `Reasoning_Agent.py`: 推理agent，包含综合置信度计算

## 运行命令

```bash
# 运行基本分析
python update.py

# 运行示例分析
python example_with_confidence.py
```

## 注意事项

1. 置信度分数范围是0-1，表示0%-100%
2. 高置信度不一定意味着结果完全正确，但表示分析过程更可靠
3. 低置信度可能表示输入数据质量差或模型不确定性高
4. 建议结合多个置信度指标来评估结果的可靠性 