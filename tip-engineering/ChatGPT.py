import openai

with open('./openai-key.txt', encoding='utf-8') as f:
    key = f.read()

class ChatGPT:
    def __init__(self):
        openai.api_key = key
        openai.api_base = "https://one.gptgod.work/v1"
        self.message = []

    def chat(self, message):
        pass
