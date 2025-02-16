import requests


def generate_video(prompt: str, api_key: str) -> dict:
    """
    Calls the RunwayML API to generate a video from the provided text description (prompt).

    Parameters:
        prompt (str): Text prompt to describe the video.
        api_key (str): Your RunwayML API key.

    Returns:
        dict: Response from the API with video URL or metadata.
    """

    # Define the RunwayML API endpoint for text-to-video (you need to replace this with the correct endpoint for your model)
    endpoint = "https://api.runwayml.com/v1/your-text-to-video-model"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    # Payload with the description (prompt) for video generation
    payload = {
        "prompt": prompt,
        "duration": 10  # Example: video duration in seconds
    }

    # Make the POST request to generate the video
    response = requests.post(endpoint, headers=headers, json=payload)

    if response.status_code == 200:
        video_data = response.json()
        return video_data  # Contains video URL or metadata
    else:
        return {"error": f"Failed to generate video: {response.status_code}, {response.text}"}

"""
# Example usage
api_key = "your-runwayml-api-key"  # Replace with your actual API key from RunwayML
prompt = "A beautiful forest scene with sunlight streaming through the trees, birds flying around."
video_response = generate_video_from_text(prompt, api_key)

print(video_response)
"""