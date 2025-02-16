import time
import requests

HF_TOKEN = "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"
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}


def generate_image(description):
    prompt = f"Create an image based on the following description: {description}. The image should reflect the elements described clearly, with proper composition and details."
    payload = {"inputs": prompt}

    # Retry logic
    retries = 5
    for _ in range(retries):
        try:
            response = requests.post(API_URL, headers=headers, json=payload)

            if response.status_code == 200:
                return response.content
            elif response.status_code == 503:
                # Handle the model loading case
                error_info = response.json()
                estimated_time = error_info.get('estimated_time', 0)
                print(f"Model is still loading. Retrying in {estimated_time:.2f} seconds...")
                time.sleep(estimated_time)  # Wait for the model to load
            else:
                print(f"Error: {response.status_code}")
                print(response.json())
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    print("Image generation failed after retries.")
    return None


# Example Usage
#llama_description = "A fluffy dog on a meadow."
#image_data = generate_image(llama_description)

#if image_data:
    # Save Image
    #with open("generated_image.png", "wb") as file:
        #file.write(image_data)
    #print("Image saved as generated_image.png")
#else:
    #print("Image generation failed.")
