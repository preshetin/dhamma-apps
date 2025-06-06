
import os
from flask import Blueprint, request
from utils.shared_functions import get_answer_from_document, send_message, send_slack_message, send_welcome_message

telegram_children_bp = Blueprint('telegram_children', __name__)


TELEGRAM_BOT_TOKEN_CHILDREN_COURSES_ORG = os.environ.get(
    'TELEGRAM_BOT_TOKEN_CHILDREN_COURSES_ORG')


@telegram_children_bp.route('/webhook-children-courses-org', methods=['POST'])
def webhook_children_courses_org():
    bot_token = TELEGRAM_BOT_TOKEN_CHILDREN_COURSES_ORG
    update = request.get_json()
    if 'message' in update and 'text' in update['message']:
        chat_id = update['message']['chat']['id']
        user_message = update['message']['text']
        user_info = update['message']['from']
        user_first_name = user_info.get('first_name', '')
        user_last_name = user_info.get('last_name', '')
        user_username = user_info.get('username', '')


        if user_message == '/start':
            send_welcome_message(chat_id, bot_token)
            return {'statusCode': 200}
        

        # Define the index and namespace for Pincone vector database
        index_name = "children-courses-org"
        namespace = "children-courses-org"

        response = get_answer_from_document(
            user_message, index_name, namespace)

        bot_token = TELEGRAM_BOT_TOKEN_CHILDREN_COURSES_ORG
        send_message(chat_id, response, bot_token)

        if user_username != 'preshetin':
            send_slack_message(user_username, index_name, user_message)

    # Handle button callbacks
    elif 'callback_query' in update:
        chat_id = update['callback_query']['message']['chat']['id']
        callback_data = update['callback_query']['data']
        user_info = update['callback_query']['from']
        user_username = user_info.get('username', '')
        
        # Send acknowledgment message
        send_message(chat_id, f"Обрабатываю вопрос: {callback_data}...", bot_token)

        # Define the index and namespace for Pincone vector database
        index_name = "children-courses-org"
        namespace = "children-courses-org"

        response = get_answer_from_document(
            callback_data, index_name, namespace)

        send_message(chat_id, response, bot_token)

        if user_username != 'preshetin':
            send_slack_message(user_username, index_name, callback_data)
        
    return '', 200
