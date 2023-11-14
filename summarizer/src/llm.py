# from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
import tiktoken
from dotenv import load_dotenv

import prompts

load_dotenv("./../.env")  # OPENAI_API_KEY
model = ChatOpenAI(model_name="gpt-4", temperature=0)
# model = ChatOpenAI(model_name="gpt-4-1106-preview")
tokenizer = tiktoken.get_encoding("cl100k_base")


def translate(text: str) -> str:
    translate_prompt = PromptTemplate(
        input_variables=["text"], template=prompts.translate_template
    )
    translate_chain = translate_prompt | model | StrOutputParser()
    translation = translate_chain.invoke({"text": text})
    return translation


def summarize(text: str) -> str:
    summary_prompt = PromptTemplate(
        input_variables=["text"], template=prompts.summary_template
    )
    summary_chain = summary_prompt | model | StrOutputParser()
    summary = summary_chain.invoke({"text": text})
    return summary


def tiktoken_len(text: str) -> int:
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
