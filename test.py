import gradio as gr
from langchain.llms.ollama import Ollama
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model='llama3.2')


def echo(message, history):
    ans = llm(message)
    print(ans)
    return ans


demo = gr.ChatInterface(fn=echo,type='messages',examples=["hello", "hola", "merhaba"])
demo.launch(share=True)