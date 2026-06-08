import torch
import json_repair
from transformers import AutoProcessor, AutoModelForCausalLM
from peft import PeftModel


BASE_MODEL_ID = "google/gemma-3-4b-it"
LORA_MODEL_ID = "AmineTibari/accounting-ocr-lora"

PROMPT = """
You are a professional OCR Details Extractor.
Extract the invoice details into a JSON format exactly as shown in the output.
Do not generate any introduction or conclusion.
""".strip()


processor = None
model = None


def load_model():
    global processor, model

    if model is not None and processor is not None:
        return model, processor

    processor = AutoProcessor.from_pretrained(BASE_MODEL_ID)

    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_ID,
        device_map="auto",
        torch_dtype="auto"
    ).eval()

    model = PeftModel.from_pretrained(
        base_model,
        LORA_MODEL_ID
    ).eval()

    return model, processor


def extract_invoice(image_path: str):
    model, processor = load_model()

    messages = [
        {
            "role": "system",
            "content": [
                {"type": "text", "text": "You are a helpful assistant."}
            ]
        },
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image_path},
                {"type": "text", "text": PROMPT}
            ]
        }
    ]

    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt"
    ).to(model.device)

    input_len = inputs["input_ids"].shape[-1]

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=1024,
            do_sample=False,
            use_cache=True
        )

    generated_tokens = outputs[0][input_len:]

    decoded = processor.decode(
        generated_tokens,
        skip_special_tokens=True
    )

    try:
        return json_repair.loads(decoded)
    except Exception:
        return {
            "error": "Could not parse model output as JSON",
            "raw_output": decoded
        }