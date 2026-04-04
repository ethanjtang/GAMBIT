import torch
from dotenv import load_dotenv

from datasets import load_dataset
from transformers import LlamaForCausalLM, AutoTokenizer, DataCollatorForLanguageModeling, Trainer, TrainingArguments

# a brittle path
load_dotenv('../.env')

model_name = "openlm-research/open_llama_3b"
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
dataset = load_dataset("text", data_files="finetune.txt", split="train")
# actual code to be used outside tests
# dataset = load_dataset("ethanjtang/GAMBIT-stockfish18-selfplay", data_files=" sf18_selfplay_unique-position-bestmove-pairs.txt")

tokenizer.pad_token = tokenizer.eos_token

def tokenize(examples):
    return tokenizer(examples["text"], truncation=True, max_length=512)

dataset = dataset.map(tokenize, batched=True, remove_columns=["text"])
dataset = dataset.train_test_split(test_size=0.1)  # type: ignore[union-attr]

print(dataset)

data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)  # type: ignore[call-arg]

model = LlamaForCausalLM.from_pretrained(
    model_name, torch_dtype=torch.float16, device_map='auto',
    # offload_folder='./offload'
    # disable offload folder when running on computer with an actual good GPU
)

training_args = TrainingArguments(  # type: ignore[call-arg]
    output_dir="open-llama-3b-finetuned",
    num_train_epochs=10,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    gradient_checkpointing=True,
    # bf16=False,
    # Use True on computers with GPUs!
    bf16=True,
    learning_rate=2e-5,
    logging_steps=1,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    remove_unused_columns=False,
    report_to="none", # disable wandb logging
    include_num_input_tokens_seen=True # print number of tokens used
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    processing_class=tokenizer,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

trainer.train()
trainer.save_model("open-llama-3b-finetuned/final")
tokenizer.save_pretrained("open-llama-3b-finetuned/final")

path = "open-llama-3b-finetuned/final"
tokenizer = AutoTokenizer.from_pretrained(path)
model = LlamaForCausalLM.from_pretrained(path, torch_dtype=torch.float16, device_map="auto")

inputs = tokenizer("GAMING GAMING GAMING\n", return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=100)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))