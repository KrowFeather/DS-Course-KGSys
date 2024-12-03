import gradio as gr
from langchain_ollama import OllamaLLM, ChatOllama

llm = ChatOllama(model='llama3.2')


def echo(message, history):
    ans = llm.stream(message)
    msg = ''
    for chunk in ans:
        msg += chunk.content
        yield msg


demo = gr.ChatInterface(fn=echo,type='messages',examples=["hello", "hola", "merhaba"])
demo.launch(share=True)