import requests
import os

class LLMService:

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "meta-llama/llama-3-8b-instruct"

    def generate(self, messages):

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages
        }

        try:
            res = requests.post(self.url, headers=headers, json=payload)
            data = res.json()

            return data["choices"][0]["message"]["content"]

        except Exception as e:
            print("❌ LLM Error:", e)
            return "ERROR"