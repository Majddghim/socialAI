import requests

API_KEY = "key_d6a3773658a01c357abcdd4583107c4693e82c916e2079fe0738d2e8dcfce5573d16ae850a71e5cff951e47488e89284c2b956064c6e901ddf70b48c05dcea3f"
API_URL = "https://api.runwayml.com/v1/models/stable-video-diffusion/generate"

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def generate_ai_video(prompt):
    data = {"prompt": prompt, "num_frames": 16}
    response = requests.post(API_URL, headers=headers, json=data)
    return response.json()  # Returns video URL

video_response = generate_ai_video("A futuristic city with neon lights")
print(video_response)
