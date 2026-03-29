import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("API KEY IS MISSING")
else:
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        models = response.json().get("models", [])
        with open("models_list.txt", "w") as f:
            for m in models:
                methods = m.get("supportedGenerationMethods", [])
                if "embedContent" in methods:
                    f.write(f"- {m['name']} (supports embedding)\n")
                else:
                    f.write(f"- {m['name']}\n")
    else:
        print(f"Error calling API: {response.text}")
