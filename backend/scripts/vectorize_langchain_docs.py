import os
import json

import boto3
from langchain.document_loaders import ReadTheDocsLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
import tiktoken


persist_directory = "db"
tokenizer = tiktoken.get_encoding("cl100k_base")


def _get_api_keys() -> str:
    session = boto3.Session()
    client = session.client("secretsmanager", region_name="eu-west-1")
    secret_string = client.get_secret_value(
        SecretId="eve-project-a9562e1a1783b0e4"
    ).get("SecretString")
    secret = json.loads(secret_string)
    return secret["openai_api_key"], secret["cohere_api_key"]


os.environ["OPENAI_API_KEY"], _ = _get_api_keys()


def tiktoken_len(text):
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)


def tiktoken_cost(docs):
    token_counts = [tiktoken_len(doc.page_content) for doc in docs]
    print(
        f"""Sum: {sum(token_counts)}
Min: {min(token_counts)}
Avg: {int(sum(token_counts) / len(token_counts))}
Max: {max(token_counts)}
Cost: ${sum(token_counts) * 0.0001 / 1000}"""
    )


def chunk_docs(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=20,
        length_function=tiktoken_len,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = text_splitter.split_documents(docs)
    print(f"Number of chunks: {len(chunks)}")
    return chunks


def main():
    if not os.path.exists(persist_directory):
        # Load docs
        print("Loading docs...")
        loader = ReadTheDocsLoader("rtdocs")
        docs = loader.load()
        print(f"Total number of Documents: {len(docs)}")

        # Check embedding cost
        print("Costs for Embedding Documents:")
        tiktoken_cost(docs)

        # Chunk docs
        print("Chunking docs...")
        chunks = chunk_docs(docs)

        # Generate or load embeddings and vector store
        print("Creating embeddings...")
        embedding = OpenAIEmbeddings()
        total_length = len(chunks)
        batch_size = 64

        for batch_start in range(0, total_length, batch_size):
            batch_end = min(batch_start + batch_size, total_length)
            batch_texts = chunks[batch_start:batch_end]
            Chroma.from_documents(
                documents=batch_texts,
                embedding=embedding,
                persist_directory=persist_directory,
            )
            print(f"Inserted {batch_end}/{total_length} chunks")
        print(f"Completed vectorizing docs.")


if __name__ == "__main__":
    main()
