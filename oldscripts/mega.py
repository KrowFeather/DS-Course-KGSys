import os.path

from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM, ChatOllama

embedding_model_dict = {
    'ernie-tiny':'nghuyong/ernie-3.0-nano-zh',
    'ernie-base': 'nghuyong/ernie-3.0-base-zh',
    'text2vec': 'GanymedeNil/text2vec-large-chinese',
    'text2vec2': 'uer/sbert-base-chinese-nli',
    'text2vec3': 'shibing624/text2vec-base-chinese'
}

def load_document(dir):
    loader = DirectoryLoader(dir)
    doc = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=256,chunk_overlap=0)
    split_docs = text_splitter.split_documents(doc)
    print(split_docs[:2])
    return split_docs

def load_embedding_mode(model_name='ernie-tiny'):
    encode_kwargs = {'normalize_embeddings': False}
    model_kwargs = {'device': 'cpu'}
    return HuggingFaceEmbeddings(
        model_name=embedding_model_dict[model_name],
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )

def store_chroma(docs,embeddings,persistent_directory='VectorStore'):
     db = Chroma.from_documents(docs,embeddings,persist_directory=persistent_directory)
     return db


embeddings = load_embedding_mode('text2vec')
if not os.path.exists('VectorStore'):
    documents = load_document('../data/nbooks')
    db = store_chroma(documents,embeddings)
else:
    db = Chroma(persist_directory='./VectorStore', embedding_function=embeddings)

llm = ChatOllama(model='llama3.2')
retriever = db.as_retriever()

template = '''
你现在是位中文数据结构与算法的助教，所以请以中文回答下面的问题，并且不要输出“根据给出的文本”这种类似的话，直接给出结果
{summaries}
{question}
'''

chain = RetrievalQAWithSourcesChain.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={
        "prompt": PromptTemplate(
            template=template,
            input_variables=["summaries","question"],
        ),
    },
)
response = chain.invoke({'question':'什么是线性表'})
print(response['answer'])
