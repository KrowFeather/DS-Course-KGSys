import pandas as pd
from langchain_ollama import OllamaEmbeddings
# df = pd.read_excel('./ds.xlsx')
# df.to_csv('./ds.csv', index=False)

from py2neo import Graph, Node

# 连接数据库
# graph = Graph('http://localhost:7474', username='neo4j', password='123456') # 旧版本
graph = Graph('neo4j://localhost:7687', auth=('neo4j', '12345678'))
graph.delete_all()
df = pd.read_csv('ds.csv')
df1 = pd.DataFrame()
for i in df.index:
    d = df.loc[i,'description']
    embedding = OllamaEmbeddings(model='llama3.2').embed_query(d)
    df1 = df1._append({'source':df.loc[i,'name'],"desc_embed":embedding},ignore_index=True)
df1.to_csv('./embeddings.csv',index=False)
# 删除所有已有节点
for i in df.index:
    graph.create(Node('concept',source=df.loc[i,'name'],description =df.loc[i,'description']))
    print(graph.nodes)
    print(df.iloc[i,:])

graph.run('''
LOAD CSV WITH HEADERS
FROM 'file:///D:/project/python/DS-KGSys/embeddings.csv'
AS row
MATCH (m:concept {source: row.source})
CALL db.create.setNodeVectorProperty(m, 'descriptionEmbedding', apoc.convert.fromJsonList(row.desc_embed))
RETURN count(*)
''')
graph.run("DROP INDEX conceptDesc IF EXISTS")
graph.run('''
CREATE VECTOR INDEX conceptDesc IF NOT EXISTS
FOR (m:concept)
ON m.descriptionEmbedding
OPTIONS {indexConfig: {
    `vector.dimensions`: 3072,
    `vector.similarity_function`: 'cosine'
}}
''')