import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.ibm import WatsonxLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def initialize_settings(api_key, project_id, url):
    # Setup IBM Watsonx (The Brain)
    llm = WatsonxLLM(
       model_id="ibm/granite-3-8b-instruct",
        url=url,
        apikey=api_key,
        project_id=project_id,
        temperature=0.2, # Key for Groundedness
        max_new_tokens=512
    )
    # Setup Local Embedding (Privacy-Preserving)
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    Settings.llm = llm
    Settings.embed_model = embed_model
    return llm

def process_and_index_docs(directory_path):
    documents = SimpleDirectoryReader(directory_path).load_data()
    index = VectorStoreIndex.from_documents(documents)
    return index.as_query_engine(streaming=True)
