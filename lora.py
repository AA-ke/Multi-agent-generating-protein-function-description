#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Phi-3 LoRA Fine-tuning for Bioinformatics QA Dataset (Fixed Version)
# Dependencies: pip install transformers datasets peft accelerate bitsandbytes torch

import json
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
import os
import warnings

warnings.filterwarnings("ignore")


class BiostarsDataProcessor:
    """处理Biostars数据集为微调格式"""

    def __init__(self, json_file):
        self.json_file = json_file

    def load_and_process_data(self, strategy="mixed"):
        """
        加载并处理JSON数据
        strategy: 处理无答案帖子的策略
        - "skip": 跳过无答案帖子
        - "template": 为无答案帖子生成模板回答
        - "mixed": 混合策略，包含有答案和无答案的帖子
        """
        with open(self.json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        processed_data = []
        stats = {
            'total': len(data),
            'with_answers': 0,
            'without_answers': 0,
            'generated_samples': 0,
            'skipped': 0
        }

        for item in data:
            # 跳过无效数据
            if not item.get('question') or len(item['question'].strip()) < 10:
                stats['skipped'] += 1
                continue

            title = item.get('title', '').strip()
            question = item.get('question', '').strip()
            answers = item.get('answers', [])
            url = item.get('url', '')

            # 过滤有效答案
            valid_answers = [ans.strip() for ans in answers if ans.strip() and len(ans.strip()) > 20]

            if valid_answers:
                # 有答案的帖子
                stats['with_answers'] += 1

                # 使用最长的答案作为最佳答案
                best_answer = max(valid_answers, key=len)
                prompt = self._format_prompt(title, question)
                response = best_answer

                processed_data.append({
                    'text': self._format_training_text(prompt, response),
                    'type': 'with_answer',
                    'url': url
                })
                stats['generated_samples'] += 1

                # 如果有多个答案，也可以使用其他答案
                for i, answer in enumerate(valid_answers[1:], 1):
                    if len(answer) > 50:  # 只要较长的答案
                        prompt_multi = self._format_prompt(title, question, f"Answer {i + 1}")
                        processed_data.append({
                            'text': self._format_training_text(prompt_multi, answer),
                            'type': 'multi_answer',
                            'url': url
                        })
                        stats['generated_samples'] += 1
            else:
                # 无答案的帖子
                stats['without_answers'] += 1

                if strategy == "skip":
                    continue
                elif strategy == "template":
                    # 生成模板回答
                    template_response = self._generate_template_response(title, question)
                    prompt = self._format_prompt(title, question)

                    processed_data.append({
                        'text': self._format_training_text(prompt, template_response),
                        'type': 'template_answer',
                        'url': url
                    })
                    stats['generated_samples'] += 1

                elif strategy == "mixed":
                    # 将无答案帖子转换为"寻求帮助"类型的训练样本
                    help_response = self._generate_help_seeking_response(title, question)
                    prompt = self._format_prompt(title, question)

                    processed_data.append({
                        'text': self._format_training_text(prompt, help_response),
                        'type': 'help_seeking',
                        'url': url
                    })
                    stats['generated_samples'] += 1

        # 打印统计信息
        print("=== 数据处理统计 ===")
        print(f"总帖子数: {stats['total']}")
        print(f"有答案帖子: {stats['with_answers']}")
        print(f"无答案帖子: {stats['without_answers']}")
        print(f"跳过的帖子: {stats['skipped']}")
        print(f"生成训练样本: {stats['generated_samples']}")
        print("==================")

        return processed_data

    def _generate_template_response(self, title, question):
        """为无答案的问题生成模板回答"""
        question_lower = question.lower()

        if any(word in question_lower for word in ['error', 'fail', 'problem', '错误']):
            return """I understand you're encountering an issue. Here are some general troubleshooting steps:

1. Check your input data format and file paths
2. Verify software versions and dependencies
3. Review error messages for specific clues
4. Check available memory and computational resources
5. Consult the software documentation

Could you provide more details about the specific error message or context for more targeted help?"""

        elif any(word in question_lower for word in ['how to', 'how do', 'tutorial', 'guide']):
            return """This is a great question about bioinformatics methodology. Here's a general approach:

1. Define your research question clearly
2. Prepare and quality-check your data
3. Choose appropriate tools and parameters
4. Run analysis with proper controls
5. Validate and interpret results
6. Document your workflow

For specific implementation details, I'd recommend checking the relevant software documentation or recent publications in this area."""

        elif any(word in question_lower for word in ['recommend', 'suggest', 'best', 'which']):
            return """The choice of tools/methods depends on several factors:

1. Your specific research objectives
2. Data type and size
3. Available computational resources
4. Required accuracy and sensitivity
5. Integration with existing workflows

Popular options in this area include widely-used, well-documented tools with active community support. I'd suggest reviewing recent comparative studies or asking for community recommendations with your specific requirements."""

        else:
            return """This is an interesting bioinformatics question. While I don't have a specific answer readily available, here are some suggestions:

1. Check recent publications in relevant journals
2. Consult specialized databases and resources
3. Reach out to the bioinformatics community
4. Consider similar solved problems as starting points

If you can provide more context or specific details, I'd be happy to offer more targeted guidance."""

    def _generate_help_seeking_response(self, title, question):
        """为无答案帖子生成"寻求帮助"类型的回答"""
        return f"""I see you're asking about: {title if title else 'this bioinformatics topic'}

This appears to be an open question that would benefit from community input. Here's how you might approach getting help:

1. **Provide more context**: Share your specific use case, data types, and constraints
2. **Include details**: Software versions, error messages, or examples if applicable  
3. **Show your attempts**: What have you tried so far?
4. **Specify requirements**: Computational resources, timeline, accuracy needs

The bioinformatics community is generally very helpful with well-documented questions. Consider posting on specialized forums or reaching out to domain experts."""

    def _format_prompt(self, title, question, suffix=None):
        """格式化输入提示"""
        prompt = f"<|system|>\nYou are a helpful bioinformatics expert. Answer the following question accurately and concisely.\n<|end|>\n"

        if title:
            prompt += f"<|user|>\nTitle: {title}\nQuestion: {question}"
        else:
            prompt += f"<|user|>\n{question}"

        if suffix:
            prompt += f"\n({suffix})"

        prompt += "\n<|end|>\n<|assistant|>\n"
        return prompt

    def _format_training_text(self, prompt, response):
        """格式化完整的训练文本"""
        return f"{prompt}{response}<|end|>"


class Phi3FineTuner:
    """Phi-3 LoRA微调器"""

    def __init__(self,
                 model_path="/home/ake/MultiAgent/multi-agent/phi3_128k_local/models--microsoft--Phi-3-mini-128k-instruct"):
        """
        初始化微调器
        model_path: 本地模型路径
        """
        self.model_path = model_path
        self.tokenizer = None
        self.model = None

        # 验证模型路径
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"本地模型路径不存在: {self.model_path}")

        if not os.path.isdir(self.model_path):
            raise NotADirectoryError(f"模型路径不是目录: {self.model_path}")

        print(f"使用本地模型路径: {self.model_path}")

    def setup_model_and_tokenizer(self):
        """设置模型和分词器"""
        print("加载本地tokenizer...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                padding_side="right",
                local_files_only=True
            )
            print("✓ Tokenizer加载成功")
        except Exception as e:
            print(f"✗ 加载tokenizer失败: {e}")
            raise

        # 确保有pad token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        print("加载本地模型（使用4bit量化）...")
        # 4bit量化配置
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )

        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.bfloat16,
                local_files_only=True
            )
            print("✓ 模型加载成功")
        except Exception as e:
            print(f"✗ 加载模型失败: {e}")
            raise

        # 重要：准备模型用于k-bit训练
        self.model = prepare_model_for_kbit_training(self.model)
        print(f"✓ 模型配置完成，使用路径: {self.model_path}")

    def setup_lora(self):
        """设置LoRA配置"""
        print("设置LoRA配置...")

        # LoRA配置 - 使用更保守的设置
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=8,  # 降低rank避免过拟合
            lora_alpha=16,  # 相应调整alpha
            lora_dropout=0.1,
            target_modules=[
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"
            ],
            bias="none",
        )

        self.model = get_peft_model(self.model, lora_config)

        # 确保LoRA参数需要梯度
        for name, param in self.model.named_parameters():
            if 'lora_' in name:
                param.requires_grad = True

        self.model.print_trainable_parameters()
        print("✓ LoRA配置完成")

    def prepare_dataset(self, processed_data, test_size=0.1):
        """准备数据集"""
        print("准备数据集...")

        def tokenize_function(examples):
            # 使用正确的tokenization方式
            texts = examples["text"]

            # 分词并设置labels
            tokenized = self.tokenizer(
                texts,
                truncation=True,
                padding=False,  # 不在这里padding
                max_length=1024,  # 减少序列长度
                return_tensors=None
            )

            # 设置labels为input_ids的副本
            tokenized["labels"] = tokenized["input_ids"].copy()

            return tokenized

        # 创建数据集
        dataset = Dataset.from_list(processed_data)
        dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names,
            desc="Tokenizing data"
        )

        # 分割训练和验证集
        if test_size > 0:
            split_dataset = dataset.train_test_split(test_size=test_size, seed=42)
            return split_dataset["train"], split_dataset["test"]
        else:
            return dataset, None

    def train(self, train_dataset, eval_dataset=None, output_dir="./phi3-biostars-lora"):
        """开始训练"""
        print("开始训练...")

        # 数据整理器
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,  # 不使用masked language modeling
            pad_to_multiple_of=8,
        )

        # 训练参数 - 调整为更稳定的设置
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=2,  # 减少epoch数
            per_device_train_batch_size=1,
            per_device_eval_batch_size=1,
            gradient_accumulation_steps=4,  # 减少梯度累积步数
            warmup_steps=50,  # 减少warmup步数
            learning_rate=1e-4,  # 降低学习率
            fp16=False,
            bf16=True,
            logging_steps=20,
            logging_dir=f"{output_dir}/logs",
            eval_strategy="steps" if eval_dataset else "no",
            eval_steps=100 if eval_dataset else None,
            save_steps=200,
            save_total_limit=2,
            load_best_model_at_end=True if eval_dataset else False,
            metric_for_best_model="eval_loss" if eval_dataset else None,
            greater_is_better=False,
            remove_unused_columns=True,  # 改为True
            dataloader_pin_memory=False,
            optim="paged_adamw_8bit",  # 使用paged版本
            max_grad_norm=1.0,  # 添加梯度裁剪
            dataloader_num_workers=0,  # 避免多进程问题
            report_to="none",  # 不使用wandb等
        )

        # 创建Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
        )

        # 开始训练
        try:
            trainer.train()
            print("✓ 训练完成")
        except Exception as e:
            print(f"✗ 训练过程中出错: {e}")
            raise

        # 保存模型
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)

        print(f"✓ 训练完成！模型保存在: {output_dir}")


def main(json_file="biostars_qa.json", output_dir="./phi3-biostars-lora", strategy="mixed"):
    """
    主函数
    json_file: 数据文件路径
    output_dir: 输出目录
    strategy: 处理无答案帖子的策略
    """
    print("=== Phi-3 生物信息学 LoRA 微调 (修复版本) ===")
    print(f"无答案帖子处理策略: {strategy}")

    # 设置CUDA优化
    if torch.cuda.is_available():
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        print(f"使用GPU: {torch.cuda.get_device_name()}")
        print(f"GPU内存: {torch.cuda.get_device_properties(0).total_memory / 1024 ** 3:.1f} GB")

    # 1. 处理数据
    print("1. 处理数据...")
    processor = BiostarsDataProcessor(json_file)
    processed_data = processor.load_and_process_data(strategy=strategy)

    if len(processed_data) < 10:
        print("警告：训练数据太少！建议至少100个样本")
        return

    # 2. 设置微调器
    print("2. 设置模型...")
    finetuner = Phi3FineTuner()
    finetuner.setup_model_and_tokenizer()
    finetuner.setup_lora()

    # 3. 准备数据集
    print("3. 准备数据集...")
    train_dataset, eval_dataset = finetuner.prepare_dataset(processed_data)

    print(f"训练集大小: {len(train_dataset)}")
    if eval_dataset:
        print(f"验证集大小: {len(eval_dataset)}")

    # 4. 开始训练
    print("4. 开始训练...")
    finetuner.train(train_dataset, eval_dataset, output_dir)

    print("=== 微调完成！===")


def test_finetuned_model(model_path="./phi3-biostars-lora", test_question=None):
    """测试微调后的模型"""
    print("加载微调后的模型...")

    try:
        from peft import PeftModel

        # 加载基础模型
        base_model_path = "/home/ake/MultiAgent/multi-agent/phi3_128k_local/models--microsoft--Phi-3-mini-128k-instruct"
        tokenizer = AutoTokenizer.from_pretrained(base_model_path, local_files_only=True)

        # 4bit量化配置
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )

        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch.bfloat16,
            local_files_only=True
        )

        # 加载LoRA适配器
        model = PeftModel.from_pretrained(base_model, model_path)
        print("✓ 微调模型加载成功")

    except Exception as e:
        print(f"✗ 加载微调模型失败: {e}")
        return

    if test_question is None:
        test_question = "How do I analyze RNA-seq data using DESeq2?"

    # 格式化输入
    prompt = f"<|system|>\nYou are a helpful bioinformatics expert. Answer the following question accurately and concisely.\n<|end|>\n<|user|>\n{test_question}\n<|end|>\n<|assistant|>\n"

    # 生成回答
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    assistant_response = response.split("<|assistant|>")[-1].strip()

    print("=" * 50)
    print("问题:", test_question)
    print("=" * 50)
    print("回答:", assistant_response)
    print("=" * 50)


if __name__ == "__main__":
    # 确保有JSON文件
    if not os.path.exists("biostars_qa.json"):
        print("错误：未找到 biostars_qa.json 文件")
        print("请先运行爬虫脚本生成数据")
    else:
        # 选择处理策略
        print("请选择无答案帖子处理策略:")
        print("1. skip - 跳过无答案帖子")
        print("2. template - 生成模板回答")
        print("3. mixed - 混合策略")

        choice = input("请输入选择 (1/2/3, 默认为1): ").strip()
        strategy_map = {"1": "skip", "2": "template", "3": "mixed"}
        strategy = strategy_map.get(choice, "skip")

        # 开始微调
        main("biostars_qa.json", strategy=strategy)

        # 询问是否测试
        test_choice = input("是否测试微调后的模型? (y/n, 默认为n): ").strip().lower()
        if test_choice == 'y':
            print("\n=== 测试微调后的模型 ===")
            test_finetuned_model()