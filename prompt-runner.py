import requests
import json

API_KEY = "sk-1d543ab9361542a4a0596e6b85fc715e"

PROMPT_FILE = "Prompts/01_architecture-utf8.txt"


MODEL = "deepseek-coder"

def read_prompt(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()

def send_prompt(prompt):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print("🚨 API Error:", response.status_code)
        print(response.text)
        return None

if __name__ == "__main__":
    prompt_text = read_prompt(PROMPT_FILE)
    print("📨 Sending prompt to DeepSeek...\n")
    result = send_prompt(prompt_text)
    
    if result:
        print("🧠 DeepSeek Response:\n")
        print(result)
