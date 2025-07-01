import requests

API_KEY = "sk-1d543ab9361542a4a0596e6b85fc715e"
MODEL = "deepseek-chat"
ENDPOINT = "https://api.deepseek.com/v1/chat/completions"
PROMPT_FILE = "main.py"  
OUTPUT_FILE = "main.py"

# Load the prompt
with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    user_prompt = f.read()

# Compose the payload
payload = {
    "model": MODEL,
    "temperature": 0.2,
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant that always replies in English and writes clean, idiomatic Python code with clear inline comments and docstrings when relevant."
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print("📨 Sending prompt to DeepSeek...\n")
response = requests.post(ENDPOINT, headers=headers, json=payload)

if response.status_code == 200:
    result = response.json()["choices"][0]["message"]["content"]
    
    # Display result
    print("🧠 DeepSeek Response:\n")
    print(result)

    # Optional: Write to file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write(result)
    print(f"\n✅ Saved to {OUTPUT_FILE}")

else:
    print(f"❌ Error {response.status_code}:\n")
    print(response.text)
