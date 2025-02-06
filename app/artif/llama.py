import requests

# Your Hugging Face API Token
HF_TOKEN = "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"

# LLaMA model endpoint (choose a free one like Meta's LLaMA 2 7B)
API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"

headers = {"Authorization": f"Bearer {HF_TOKEN}"}


def generate_text(prompt):
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


def extract(description, nbr):
    """
    Generate a number of posts based on the given video description.
    """
    #prompt = f"From this text '{description}', generate {nbr} short social media posts based on it. Format the response as a numbered list."
    prompt = f"generate only 1 short reduced recap of 100 caracters from this text :  '{description}'"

    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        print("Full API Response:", result)  # Debugging step

        # Ensure response is a list and extract text
        if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
            generated_text = result[0]["generated_text"]
            print("Generated Text:", generated_text)  # Debugging step

            # Try splitting by numbering (e.g., '1.', '2.', etc.)
            posts = [post.strip() for post in generated_text.split("\n") if post.strip()]
            return posts[:nbr]  # Return only the required number of posts

        return {"error": "Unexpected response format", "details": result}

    return {"error": "Failed to generate posts", "details": response.json()}

# Example usage
#description = "AI automation is transforming industries by increasing efficiency and reducing human errors."
#nbr = 5
#generated_posts = extract(description, nbr)

# Print the generated posts
#for i, post in enumerate(generated_posts, 1):
#    print(f"Post {i}: {post}")
# Example usage
#prompt = "Generate a short social media post about AI automation."
#result = generate_text(prompt)

#print(result)
