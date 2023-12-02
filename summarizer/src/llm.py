import json

import boto3
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser

import prompts


def _get_openai_api_key() -> str:
    session = boto3.Session()
    ssm = session.client("ssm", region_name="eu-west-1")
    secret_name = (
        ssm.get_parameter(Name="/eve-project/secret-name")
        .get("Parameter", {})
        .get("Value")
    )
    secretsmanager = session.client("secretsmanager", region_name="eu-west-1")
    secret_string = secretsmanager.get_secret_value(SecretId=secret_name).get(
        "SecretString"
    )
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
