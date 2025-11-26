from langchain_core.runnables import RunnableLambda

# 你的本地模型
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

tokenizer = AutoTokenizer.from_pretrained("../phi3-biostars-merged")
model = AutoModelForCausalLM.from_pretrained("../phi3-biostars-merged")
llm_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0)

# 封装为 LangChain Runnable（用于 LangGraph 节点）
local_phi3_agent = RunnableLambda(
    lambda x: {"response": llm_pipeline(x["input"], max_new_tokens=512)[0]["generated_text"]}
)

from langgraph.graph import StateGraph

# 创建 Graph（只一个节点，当然你可以继续扩展更多）
graph_builder = StateGraph(dict)

graph_builder.add_node("phi3_agent", local_phi3_agent)
graph_builder.set_entry_point("phi3_agent")

graph = graph_builder.compile()

result = graph.invoke({"input": "What is synthetic biology?"})
print(result["response"])


