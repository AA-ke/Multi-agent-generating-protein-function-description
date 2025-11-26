from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

# 加载未微调模型
tokenizer0 = AutoTokenizer.from_pretrained("./phi3_128k_local/models--microsoft--Phi-3-mini-128k-instruct")
model0 = AutoModelForCausalLM.from_pretrained("./phi3_128k_local/models--microsoft--Phi-3-mini-128k-instruct")
generator0 = pipeline("text-generation", model=model0, tokenizer=tokenizer0, device=0)

# # 加载微调后模型
# tokenizer1 = AutoTokenizer.from_pretrained("./phi3-biostars-merged")
# model1 = AutoModelForCausalLM.from_pretrained("./phi3-biostars-merged")
# generator1 = pipeline("text-generation", model=model1, tokenizer=tokenizer1, device=0)

prompts = [
    "How would I provide quality metrics on FASTQ files?",
    "How do I align RNA-seq data against a human reference genome?",
    # "Question: What methods were used to measure homocysteine production?\nAnswer:",
    # "Question: Summarize the effects of the supplementation on mice.\nAnswer:",
    # "Question: What conclusions were drawn about urinary metabolite 17α-SMA in children?\nAnswer:"
]

for prompt in prompts:
    print(f"Q: {prompt}")

    out_before = generator0(prompt, max_length=100, do_sample=True, top_p=0.9, top_k=50)
    answer_before = out_before[0]['generated_text'][len(prompt):].strip()
    print(f"Before LoRA: {answer_before}")

    # out_after = generator1(prompt, max_length=200, do_sample=True, top_p=0.9, top_k=50)
    # answer_after = out_after[0]['generated_text'][len(prompt):].strip()
    # print(f"After LoRA: {answer_after}")

    print("-" * 50)