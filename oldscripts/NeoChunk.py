from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import Neo4jVector
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from py2neo import Graph


graph = Graph('neo4j://localhost:7687', auth=('neo4j', '12345678'))
graph.delete_all()

llm = OllamaLLM(model='llama3.2')

def load_document(dir):
    loader = DirectoryLoader(dir)
    doc = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=128, chunk_overlap=0)
    split_docs = text_splitter.split_documents(doc)
    print(split_docs[:2])
    return split_docs

documents = load_document('testbooks')
neo4j_vector = Neo4jVector.from_documents(
    documents,
    OllamaEmbeddings(model='llama3.2'),
    url='neo4j://localhost:7687',
    username='neo4j',
    password='12345678',
)

prompt = '''
你现在是位中文数据结构与算法的助教，所以请以中文回答下面的问题，并且不要输出“根据给出的文本”这种类似的话，直接给出结果
{summaries}
{question}
'''

query = "什么是数据结构三要素"

results = neo4j_vector.similarity_search(query, k=1)

chain = RetrievalQAWithSourcesChain.from_chain_type(
    OllamaLLM(model='llama3.2'),
    chain_type="stuff",
    retriever=neo4j_vector.as_retriever(),
    chain_type_kwargs = {
        "prompt": PromptTemplate(
            template=prompt,
            input_variables=["summaries", "question"],
        ),
    }
)

query = "什么是数据结构三要素"

res = chain.invoke({"question": query},return_only_outputs=True)
print(res['answer'])