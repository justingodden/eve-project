import json
import os

import boto3
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank


persist_directory = "db"


def _get_api_keys() -> str:
    session = boto3.Session()
    client = session.client("secretsmanager", region_name="eu-west-1")
    secret_string = client.get_secret_value(
        SecretId="eve-project-a9562e1a1783b0e4"
    ).get("SecretString")
    secret = json.loads(secret_string)
    return secret["openai_api_key"], secret["cohere_api_key"]


os.environ["OPENAI_API_KEY"], os.environ["COHERE_API_KEY"] = _get_api_keys()
embedding = OpenAIEmbeddings()
model = ChatOpenAI(model_name="gpt-4", temperature=0)
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)
retriever = vectordb.as_retriever(search_kwargs={"k": 20})
compressor = CohereRerank(user_agent="my-app", top_n=5)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=retriever
)
qa = RetrievalQA.from_chain_type(
    llm=model, chain_type="stuff", retriever=compression_retriever
)
