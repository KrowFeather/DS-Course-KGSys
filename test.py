import gradio as gr
from transformers import AutoModel

model_path = './pretrained_llama/pretrained_llama'
llm = AutoModel.from_pretrained(model_path)

def echo(message, history):
    ans = llm.stream(message)
    msg = ''
    for chunk in ans:
        msg += chunk.content
        yield msg


demo = gr.ChatInterface(fn=echo,type='messages',examples=["hello", "hola", "merhaba"])
demo.launch(share=True)