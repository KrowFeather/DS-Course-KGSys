import logging
import os
import sys

from langchain_ollama import OllamaLLM, OllamaEmbeddings
from llama_index.core import StorageContext, load_index_from_storage, Settings, KnowledgeGraphIndex, \
    SimpleDirectoryReader, PromptTemplate
from llama_index.graph_stores.nebula import NebulaGraphStore

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

llm = OllamaLLM(model='llama3.2', temperature=0)
embedding_model = OllamaEmbeddings(model='llama3.2')

Settings.llm = llm
Settings.embed_model = embedding_model
Settings.chunk_size = 256

os.environ["NEBULA_USER"] = "root"
os.environ[
    "NEBULA_PASSWORD"
] = "123456"
os.environ[
    "NEBULA_ADDRESS"
] = "127.0.0.1:9669"

# Assume that the graph has already been created
# Create a NebulaGraph cluster with:
# Option 0: `curl -fsSL nebula-up.siwei.io/install.sh | bash`
# Option 1: NebulaGraph Docker Extension https://hub.docker.com/extensions/weygu/nebulagraph-dd-ext
# and that the graph space is called "paul_graham_essay"
# If not, create it with the following commands from NebulaGraph's console:
# CREATE SPACE paul_graham_essay(vid_type=FIXED_STRING(256), partition_num=1, replica_factor=1);
# :sleep 10;
# USE paul_graham_essay;
# CREATE TAG entity(name string);
# CREATE EDGE relationship(relationship string);
# CREATE TAG INDEX entity_index ON entity(name(256));

space_name = "paul_graham_essay"
edge_types, rel_prop_names = ["relationship"], [
    "relationship"
]
tags = ["entity"]

documents = SimpleDirectoryReader(
    "D:/project/python/DS-KGSys/data/nbooks"
    , encoding='utf-8').load_data()

graph_store = NebulaGraphStore(
    space_name=space_name,
    edge_types=edge_types,
    rel_prop_names=rel_prop_names,
    tags=tags,
)

if os.path.exists('./storage_graph'):
    storage_context = StorageContext.from_defaults(persist_dir='./storage_graph', graph_store=graph_store)
    kg_index = load_index_from_storage(
        storage_context=storage_context,
        max_triplets_per_chunk=10,
        space_name=space_name,
        edge_types=edge_types,
        rel_prop_names=rel_prop_names,
        tags=tags,
        include_embeddings=True,
    )
else:
    storage_context = StorageContext.from_defaults(graph_store=graph_store)
    kg_index = KnowledgeGraphIndex.from_documents(
        documents=documents,
        storage_context=storage_context,
        max_triplets_per_chunk=10,
        space_name=space_name,
        edge_types=edge_types,
        rel_prop_names=rel_prop_names,
        tags=tags,
        include_embeddings=True,
    )
    kg_index.storage_context.persist(persist_dir='./storage_graph')

kg_query_engine = kg_index.as_query_engine()

# shakespeare!
qa_prompt_tmpl_str = (
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "你现在是位中文数据结构与算法的助教，所以请以中文回答下面的问题，并且不要输出“根据给出的文本”这种类似的话，用委婉的语气给出结果\n "
    "Query: {query_str}\n"
    "Answer: "
)
qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)

kg_query_engine.update_prompts(
    {"response_synthesizer:text_qa_template": qa_prompt_tmpl}
)

res = kg_query_engine.query('动态规划包含什么?')
print(res)


from pyvis.network import Network

g = kg_index.get_networkx_graph()
net = Network(notebook=True, cdn_resources="in_line", directed=True)
net.from_nx(g)
# Save the HTML to a string
try:
    html_string = net.generate_html()

# Write to a file with UTF-8 encoding
    with open("example.html", "w", encoding="utf-8") as f:
        f.write(html_string)
except Exception as e:
    print('ok')