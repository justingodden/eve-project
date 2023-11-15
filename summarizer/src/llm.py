import json

import boto3
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser

import prompts


def _get_openai_api_key() -> str:
    session = boto3.Session()
    client = session.client("secretsmanager", region_name="eu-west-1")
    secret_string = client.get_secret_value(
        SecretId="eve-project-a9562e1a1783b0e4"
    ).get("SecretString")
    secret = json.loads(secret_string)
    return secret["openai_api_key"]


model = ChatOpenAI(
    model_name="gpt-4", temperature=0, openai_api_key=_get_openai_api_key()
)


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
