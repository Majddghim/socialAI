import requests

# image generation with hugging face stable-diffusion-2 model
HF_TOKEN = ""
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def generate_image(prompt):
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content  # Returns the image bytes

# Example Usage
#prompt = "a dog in a field of flowers"
#image_data = generate_image(prompt)

# Save Image
#with open("generated_image.png", "wb") as file:
 #   file.write(image_data)

#print("Image saved as generated_image.png")
