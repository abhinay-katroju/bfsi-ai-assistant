"""Small Language Model (SLM) Fine-tuning for BFSI domain"""
import json
import logging
import torch
from pathlib import Path
from typing import Dict, List, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import Dataset

logger = logging.getLogger(__name__)

class BFSISLMTrainer:
    """Fine-tune a lightweight SLM on BFSI dataset using QLoRA"""
    
    def __init__(self, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0", device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None
        
        logger.info(f"Using device: {device}")
        logger.info(f"Model: {model_name}")
    
    def prepare_data(self, dataset_path: Path) -> Dataset:
        """Prepare dataset for training"""
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Format data for instruction fine-tuning
        formatted_data = []
        for item in data:
            text = f"""<s>[INST] {item['instruction']}
{item['input']} [/INST]
{item['output']}</s>"""
            formatted_data.append({"text": text})
        
        dataset = Dataset.from_dict({"text": [d["text"] for d in formatted_data]})
        logger.info(f"Prepared {len(dataset)} training samples")
        return dataset
    
    def load_model(self):
        """Load base model with quantization"""
        # 4-bit quantization config
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=bnb_config,
            device_map="auto"
        )
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        logger.info("Model and tokenizer loaded successfully")
    
    def setup_lora(self, r: int = 16, lora_alpha: int = 32, lora_dropout: float = 0.05):
        """Setup LoRA for efficient fine-tuning"""
        self.model = prepare_model_for_kbit_training(self.model)
        
        lora_config = LoraConfig(
            r=r,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "v_proj"],
        )
        
        self.model = get_peft_model(self.model, lora_config)
        logger.info("LoRA config applied successfully")
        self.model.print_trainable_parameters()
    
    def train(self, dataset: Dataset, output_dir: Path, num_epochs: int = 3, batch_size: int = 4):
        """Fine-tune the model"""
        training_args = TrainingArguments(
            output_dir=str(output_dir),
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=2,
            save_steps=50,
            save_total_limit=2,
            logging_steps=10,
            learning_rate=2e-4,
            weight_decay=0.001,
            warmup_steps=100,
            bf16=True,
            optim="paged_adamw_32bit",
        )
        
        trainer = SFTTrainer(
            model=self.model,
            train_dataset=dataset,
            peft_config=None,
            dataset_text_field="text",
            args=training_args,
            tokenizer=self.tokenizer,
            max_seq_length=512,
        )
        
        logger.info("Starting training...")
        trainer.train()
        logger.info("Training completed")
        
        # Save model
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        logger.info(f"Model saved to {output_dir}")
    
    @staticmethod
    def load_fine_tuned_model(model_dir: Path, base_model: str):
        """Load fine-tuned model"""
        from peft import AutoPeftModelForCausalLM
        
        model = AutoPeftModelForCausalLM.from_pretrained(
            model_dir,
            device_map="auto",
        )
        
        tokenizer = AutoTokenizer.from_pretrained(model_dir)
        logger.info(f"Fine-tuned model loaded from {model_dir}")
        return model, tokenizer


class BFSIInference:
    """Inference with fine-tuned BFSI SLM"""
    
    def __init__(self, model_dir: Optional[Path] = None, base_model: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        if model_dir and model_dir.exists():
            self.model, self.tokenizer = BFSISLMTrainer.load_fine_tuned_model(model_dir, base_model)
            self.is_fine_tuned = True
        else:
            # Fall back to base model if fine-tuned not available
            self.tokenizer = AutoTokenizer.from_pretrained(base_model)
            self.model = AutoModelForCausalLM.from_pretrained(
                base_model,
                torch_dtype=torch.bfloat16,
                device_map="auto"
            )
            self.is_fine_tuned = False
            logger.warning("Using base model (not fine-tuned)")
        
        self.device = self.model.device
    
    def generate_response(self, query: str, max_length: int = 128, temperature: float = 0.3) -> str:
        """Generate response using fine-tuned model - optimized for speed"""
        prompt = f"<s>[INST] {query} [/INST]"
        
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=200).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=1,  # Disable beam search for faster inference
                min_length=10,
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Extract response part only
        if "[/INST]" in response:
            response = response.split("[/INST]")[-1].strip()
        
        return response


if __name__ == "__main__":
    from src.config import DATA_DIR, MODELS_DIR
    
    logging.basicConfig(level=logging.INFO)
    
    # Prepare data
    dataset_path = DATA_DIR / "bfsi_dataset.json"
    output_dir = MODELS_DIR / "fine_tuned_bfsi_model"
    
    if dataset_path.exists():
        print("To fine-tune the model, run:")
        print("python -m src.model_finetuning")
    else:
        print(f"Dataset not found at {dataset_path}")
        print("Generate dataset first using: python -m src.dataset_generator")
