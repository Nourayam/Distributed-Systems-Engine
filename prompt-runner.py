import os
import requests

# === 🔐 Configuration ===
API_KEY = "sk-1d543ab9361542a4a0596e6b85fc715e"
MODEL = "deepseek-chat"
ENDPOINT = "https://api.deepseek.com/v1/chat/completions"

# === 🗂️ Project Files to Submit ===
INPUT_FILES = [
    "logging/event_logger.py",
]

OUTPUT_FILE = "logging/event_logger.py"

# === 📦 Load Code from Files ===
def load_files(file_paths):
    combined = ""
    for path in file_paths:
        if not os.path.exists(path):
            print(f"⚠️ Skipping missing file: {path}")
            continue
        with open(path, "r", encoding="utf-8") as f:
            combined += f"\n# ==== FILE: {path} ====\n"
            combined += f.read() + "\n"
    return combined

code_context = load_files(INPUT_FILES)

# === ✍️ Custom Refactoring Prompt ===
refactor_prompt = f"""
You are an expert software engineer reviewing a multi-file Python project built for distributed system simulation.

Your task is to refactor and productionize the codebase. Specifically:

1. **Fix Imports VERY URGENT PLEASE**:
   - Resolve missing or broken import statements
   - Ensure all modules can be loaded as packages (`__init__.py` if needed)

2. **Code Cleanup**:
   - Remove any redundant, duplicated, or unnecessary logic
   - Merge similar constructs where appropriate
   - Ensure modular and maintainable design

3. **Best Practices**:
   - Follow idiomatic Python (PEP 8) conventions
   - Add concise docstrings or comments when helpful
   - Ensure consistent naming conventions and type hints where sensible

4. **Production Readiness**:
   - Improve code structure for testability and scaling
   - Leave TODOs or recommendations for any deeper architectural improvements
   - Avoid breaking existing high-level functionality

5. you only use hashtags for comments not docstrings, important!!   

---

Below is the complete codebase. Reply with the fully updated and polished versions of **only** the files that were changed. Use clear `# ==== FILE: path ====` markers to segment your response.

{code_context}
"""

# === 📬 Compose Request Payload ===
payload = {
    "model": MODEL,
    "temperature": 0.2,
    "messages": [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that always responds in English and returns clean, production-quality Python."
            )
        },
        {
            "role": "user",
            "content": refactor_prompt
        }
    ]
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# === 🚀 Send Request to DeepSeek ===
print("📡 Sending full project context to DeepSeek...\n")
response = requests.post(ENDPOINT, headers=headers, json=payload)

# === 📥 Handle the Response ===
if response.status_code == 200:
    result_text = response.json()["choices"][0]["message"]["content"]
    
    print("✅ DeepSeek responded with proposed changes!\n")
    print(result_text[:1000] + "\n...")  # Preview first 1000 characters

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write(result_text)
    print(f"📁 Saved full response to: {OUTPUT_FILE}")

else:
    print(f"❌ DeepSeek API Error {response.status_code}:\n")
    print(response.text)
