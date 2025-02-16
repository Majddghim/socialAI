import requests
import json

def generate_post_description(description, llama_api_url):
    """
    Generates a social media post description with hashtags using LLaMA 3.1 API.

    :param description: The topic for generating the post description.
    :param llama_api_url: The LLaMA API endpoint URL.
    :return: Generated post description with hashtags or None if an error occurs.
    """

    # Refined prompt
    prompt = f"""
    Generate a short, engaging social media post about: {description}
    Include relevant hashtags at the end.
    Only return the post text and hashtags—no explanations, no formatting, no additional details.
    """

    payload = {
        "prompt": prompt,
        "model": "llama3.1",
    }

    try:
        response = requests.post(llama_api_url, json=payload, stream=True)

        if response.status_code == 200:
            full_response = []
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    line_data = json.loads(decoded_line)

                    if "response" in line_data:
                        full_response.append(line_data["response"])

            generated_text = " ".join(full_response).strip()

            if generated_text:
                print(f"Generated Post: {generated_text}")
                return generated_text
            else:
                print("Error: Response is empty.")
                return None

        else:
            print(f"Failed to generate post with LLaMA. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"Error generating post: {e}")
        return None

# Example usage:
#generate_post_description("The importance of consistency in success", "http://127.0.0.1:11434/api/generate")
