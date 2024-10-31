import json

from langchain_community.document_loaders import TextLoader
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_community.vectorstores.neo4j_vector import remove_lucene_chars
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
import ast
graph = Neo4jGraph(url='neo4j://localhost:7687',username='neo4j',password='12345678')

loader = TextLoader(file_path='../data/paul_graham/test.txt', encoding='utf-8')
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=250,chunk_overlap=24)
documents = text_splitter.split_documents(documents=docs)

print(documents)

llm = ChatOllama(model='llama3.2')
llm_transformer = LLMGraphTransformer(llm=llm)
graph_documents = llm_transformer.convert_to_graph_documents(documents)
print(graph_documents[0])

graph.add_graph_documents(
    graph_documents=graph_documents,
    baseEntityLabel=True,
    include_source=True
)

vector_index = Neo4jVector.from_existing_graph(
    OllamaEmbeddings(model='llama3.2'),
    search_type='hybrid',
    node_label='Document',
    text_node_properties=['text'],
    embedding_node_property='embedding',
    url='neo4j://localhost:7687',
    username='neo4j',
    password='12345678'
)

retriever = vector_index.as_retriever()

class Entities(BaseModel):
    names: list[str] | str = Field(
        description='All the concept entities that appear in the text'
    )

prompt = ChatPromptTemplate.from_messages(
    [
        (
            'system','you are extracting concept entities from the text.',
        ),
        (
            'human','use the given format to extract information from the following input:{question}, make sure the output format is a list'
        )
    ]
)
from neo4j import Driver, GraphDatabase


def initialize_fulltext_index(driver: Driver):
    with driver.session() as session:
        # Check if the index exists
        session.run("CREATE FULLTEXT INDEX entity IF NOT EXISTS FOR (n:Document) ON EACH [n.text]")
        # logger.info("Fulltext index 'entity' created or already exists")

# Initialize Neo4j driver
neo4j_driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "12345678"))

# Initialize fulltext index
initialize_fulltext_index(neo4j_driver)

entity_chain = prompt | llm.with_structured_output(Entities)

ans = entity_chain.invoke({'question':'什么是数据结构三要素'}).names
print(ans)
print(type(ans))

def generate_full_text_query(input):
    words = [el for el in remove_lucene_chars(input).split() if el]
    if not words:
        return ''
    full_text_query = ' AND '.join([f'{word}~2' for word in words])
    print('Generated Query:',full_text_query)
    return full_text_query.strip()

def graph_retriever(question):
    result=''
    entities = entity_chain.invoke({'question':question}).names
    if type(entities)==str:
        entities = ast.literal_eval(entities)
    for entity in entities:
        response = graph.query(
            '''
            CALL db.index.fulltext.queryNodes('entity',$query,{limit:2})
            YIELD node,score
            CALL {
                WITH node
                MATCH (node)-[r:!MENTIONS]->(neighbor)
                RETURN node.id + '-' + type(r) + '->' + neighbor.id AS output
                UNION ALL
                WITH node
                MATCH (node)<-[r:!MENTIONS]-(neighbor)
                RETURN neighbor.id + '-' + type(r) + '->' + node.id AS output
            }
            RETURN output LIMIT 50
            ''',
            {'query':generate_full_text_query(entity)},
        )
        result += '\n'.join([el['output'] for el in response])
    return result
#
print(graph_retriever('什么是数据结构三要素'))

def full_retriever(question):
    graph_data = graph_retriever(question)
    vector_data = [el.page_content for el in retriever.invoke(question)]
    final_data = f'''
        Graph Data:{graph_data}
        Vector Data:{'#Document '.join(vector_data)}
    '''
    return final_data

template = '''
Answer the question based on the following context:
{context}
Question:{question}
Use natural language and be concise
Answer:
'''
prompt = ChatPromptTemplate.from_template(template)

chain = (
    {
        'context': full_retriever,
        'question':RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)

print(chain.invoke(input='什么是数据结构三要素'))
print(chain.invoke(input='什么是数据'))
print(chain.invoke(input='什么是数据对象'))