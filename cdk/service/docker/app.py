import json

import streamlit as st
from aws_lambda_powertools.utilities import parameters
from langchain.llms import OpenAI


def get_openai_api_key():
    try:
        secrets_provider = parameters.SecretsProvider()
        secret = secrets_provider.get('openapi')
        api_key = json.loads(secret).get('openapi')
        return api_key
    except Exception as e:
        st.error(f'An error occurred while retrieving the secret: {e}')
        st.stop()


def generate_response(input_text: str, openai_api_key: str):
    llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
    prompt = (
        'You are Ran the Builder, an AWS Serverless Hero and a Principal Architect at CyberArk. '
        'You have a website called ranthebuilder.cloud. '
        'Answer the following question: '
    )
    response = llm(prompt + input_text)
    st.info(response)


def main():
    st.title('🦜🔗 Ran the Builder ChatBot')

    openai_api_key = get_openai_api_key()

    with st.form('my_form'):
        text = st.text_area('Enter text:', 'Ask me anything!')
        submitted = st.form_submit_button('Submit')
        if submitted:
            generate_response(text, openai_api_key)


if __name__ == '__main__':
    main()
