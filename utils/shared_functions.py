import os
from langchain_pinecone import PineconeEmbeddings, PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain import hub
from pinecone import Pinecone
import requests


def get_answer_from_document(message, index_name, namespace):
    # Initialize Pinecone
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

    # Initialize the embeddings
    model_name = 'multilingual-e5-large'
    embeddings = PineconeEmbeddings(
        model=model_name,
        pinecone_api_key=os.environ.get('PINECONE_API_KEY')
    )

    # Load the existing vector store
    docsearch = PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings,
        namespace=namespace
    )

    # Initialize the retriever
    retriever = docsearch.as_retriever()

    # Initialize the language model
    llm = ChatOpenAI(
        openai_api_key=os.environ.get('OPENAI_API_KEY'),
        model_name='gpt-4o-mini',
        temperature=0.0
    )

    # Create the retrieval chain
    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    combine_docs_chain = create_stuff_documents_chain(
        llm, retrieval_qa_chat_prompt
    )
    retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

    answer_with_knowledge = retrieval_chain.invoke({"input": message})

    return answer_with_knowledge['answer']


def send_slack_message(username, index_name, message):
    formatted_message = f"*{username}|{index_name}*: {message}"
    payload = {
        "text": formatted_message
    }
    response = requests.post(os.environ.get('SLACK_WEBHOOK_URL'), json=payload)
    if response.status_code != 200:
        print(f"Failed to send message to Slack: {
              response.status_code}, {response.text}")


def get_gpt_response(user_message):
    headers = {
        'Authorization': f'Bearer {os.environ.get('OPENAI_API_KEY')}',
        'Content-Type': 'application/json',
    }
    data = {
        'model': 'gpt-3.5-turbo',  # or any other model you want to use
        'messages': [{'role': 'user', 'content': user_message}],
    }

    OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

    response = requests.post(OPENAI_API_URL, headers=headers, json=data)
    response_json = response.json()

    # Extract the assistant's reply
    if 'choices' in response_json and len(response_json['choices']) > 0:
        return response_json['choices'][0]['message']['content']
    else:
        return "Sorry, I couldn't get a response from the AI."


def send_message(chat_id, text, bot_token):
    """Send Telegram message

    Args:
        chat_id (int): Chat ID from Telegram webhook payload
        text (str): Text message to be sent in the message
        bot_token (str): Telegram bot token
    """

    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'  # Optional: use Markdown formatting
    }
    requests.post(url, json=payload)
