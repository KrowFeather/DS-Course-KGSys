from gradio_client import Client, handle_file

client = Client("http://127.0.0.1:7863/")
# client.predict(
#   chatbot=[],
#   role="",
#   query="user",
#   api_name="/append"
# )

result = client.predict(
  chatbot=[["请你给我出一道关于线性表类型的数据结构与算法的多选题",'']],
  system=None,
  tools="",
  image=None,
  video=None,
  max_new_tokens=None,
  top_p=512,
  temperature=0.7,
  api_name="/stream"
)
print(result)
