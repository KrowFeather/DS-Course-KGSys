from langchain.chains import RetrievalQA
from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM,OllamaEmbeddings

llm = OllamaLLM(model='llama3.2')

embedding_provider = OllamaEmbeddings(model='llama3.2')

graph = Neo4jGraph(
    url="neo4j://localhost:7687",
    username="neo4j",
    password="12345678"
)

db = Neo4jVector.from_existing_index(
    embedding=embedding_provider,
    graph=graph,
    index_name="conceptDesc",
    embedding_node_property="descriptionEmbedding",
    text_node_property="description",
)
prompt = '''
你现在是位中文数据结构与算法的助教，所以请以中文回答下面的问题，并且不要输出“根据给出的文本”这种类似的话，直接给出结果
{summaries}
{question}
'''
ans = db.similarity_search(query='什么是数据对象',k=1)
print(ans)
plot_retriever = RetrievalQAWithSourcesChain.from_chain_type(
    llm=llm,
    chain_type='stuff',
    retriever=db.as_retriever(),
    chain_type_kwargs = {
        "prompt": PromptTemplate(
            template=prompt,
            input_variables=["summaries", "question"],
        ),
    }
)

response = plot_retriever.invoke(
    {"question": "什么是数据结构的三要素"}
)
#
print(response)