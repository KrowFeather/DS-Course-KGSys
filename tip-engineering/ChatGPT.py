import openai

with open('./openai-key.txt', encoding='utf-8') as f:
    key = f.read()

class ChatGPT:
    def __init__(self):
        openai.api_key = key
        openai.api_base = "https://xiaoai.plus/v1"
        self.messages = []

    def chat(self, message):
        self.messages.append({"role": "user", "content": message})
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=self.messages
        )
        return response["choices"][0]["message"]
