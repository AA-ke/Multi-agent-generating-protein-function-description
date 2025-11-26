from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained(
    "./phi3_128k_local/models--microsoft--Phi-3-mini-128k-instruct",
    device_map="auto",
    torch_dtype="auto"
)

model = PeftModel.from_pretrained(base_model, "./phi3-biostars-lora")
merged_model = model.merge_and_unload()

merged_model.save_pretrained("./phi3-biostars-merged")
tokenizer = AutoTokenizer.from_pretrained("./phi3-biostars-lora")
tokenizer.save_pretrained("./phi3-biostars-merged")
