# not working



from transformers import AutoModelForCausalLM, AutoTokenizer


import torch

# Load the DeepSeek model and tokenizer
def load_deepseek_model(model_name="deepseek-ai/deepseek-llm"):
    """
    Load the DeepSeek model and tokenizer.
    Replace 'deepseek-ai/deepseek-llm' with the correct model path if you're using a custom model.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    return model, tokenizer

# Generate text using DeepSeek
def generate_text(model, tokenizer, prompt, max_length=100):
    """
    Generate text based on a prompt using the DeepSeek model.
    """
    # Tokenize the input prompt
    inputs = tokenizer(prompt, return_tensors="pt")

    # Generate text
    outputs = model.generate(
        inputs["input_ids"],
        max_length=max_length,
        num_return_sequences=1,
        no_repeat_ngram_size=2,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.7,
    )

    # Decode the generated text
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_text

# Main function to test DeepSeek
if __name__ == "__main__":
    # Load the DeepSeek model
    model, tokenizer = load_deepseek_model()

    # Define a prompt
    prompt = "Explain the benefits of using AI in social media marketing:"

    # Generate text
    generated_text = generate_text(model, tokenizer, prompt)

    # Print the generated text
    print("Generated Text:")
    print(generated_text)