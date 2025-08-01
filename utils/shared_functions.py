import os
from chatgpt_md_converter import telegram_format
from langchain_pinecone import PineconeEmbeddings, PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
import requests


def get_answer_from_document(message, index_name, namespace):
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
    custom_prompt = """You are a helpful assistant that answers questions based on provided context.

    Try to include links to files or documents if the context contains them.
    
    <context>
    {context}
    </context>
    
    Answer the question based on the context. If you cannot find the answer in the context, say "Я не могу ответить в рамках моих знаний." Do not make up information."""

    retrieval_qa_chat_prompt = ChatPromptTemplate.from_messages([
        ("system", custom_prompt),
        ("user", "{input}"),
    ])
    
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

    formatted_text = telegram_format(text)

    payload = {
        'chat_id': chat_id,
        'text': formatted_text,
        'parse_mode': 'html' 
    }
    requests.post(url, json=payload)


def send_welcome_message(chat_id, bot_token):
    """Send welcome message with example buttons
    
    Args:
        chat_id (int): Chat ID from Telegram webhook payload
        bot_token (str): Telegram bot token
    """
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    
    # Define example messages that will appear as buttons
    example_messages = [
        "Как организовать детский курс?",
        "Какие есть роли у служащих?",
        "В какие игры играть с детьми?",
        "Материалы для печати"
    ]
    
    # Create inline keyboard markup with buttons
    keyboard = {
        'inline_keyboard': [
            [{'text': msg, 'callback_data': msg}] for msg in example_messages
        ]
    }
    
    welcome_text = "👋 Добро пожаловать!\n\n Я помогу вам узнать больше, как проводить детские курсы Анапаны, как их преподает С.Н. Гоенка-джи.\n\nВот примеры вопросов, которые вы можете задать ⬇️"
    
    payload = {
        'chat_id': chat_id,
        'text': welcome_text,
        'reply_markup': keyboard
    }
    
    requests.post(url, json=payload)
