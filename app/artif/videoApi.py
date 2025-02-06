import requests

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-video-diffusion-txt2vid"
headers = {"Authorization": "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"}

def generate_video(prompt):
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()  # Returns video URL or data

prompt = "A futuristic city with flying cars and neon lights"
video_response = generate_video(prompt)
print(video_response)
