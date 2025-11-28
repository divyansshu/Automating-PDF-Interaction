
import os
import requests
from dotenv import load_dotenv

# Load env vars
load_dotenv()

def test_http():
    hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    repo_id = "google/flan-t5-large"
    # Trying the router URL structure
    api_url = f"https://router.huggingface.co/hf-inference/models/{repo_id}"
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    print(f"Testing URL: {api_url}")
    
    payload = {
        "inputs": "What is the capital of France?",
        "parameters": {"max_new_tokens": 50}
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_http()
