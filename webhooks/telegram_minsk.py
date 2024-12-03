# webhooks/payment.py
import os
from flask import Blueprint, request
from utils.minsk_agent import run_agent
from utils.shared_functions import get_answer_from_document, send_message, send_slack_message

telegram_minsk_bp = Blueprint('telegram_minsk', __name__)

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')


@telegram_minsk_bp.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        user_message = update['message']['text']
        user_info = update['message']['from']
        user_first_name = user_info.get('first_name', '')
        user_last_name = user_info.get('last_name', '')
        user_username = user_info.get('username', '')

        # Define the index and namespace for Pincone vector database
        index_name = "minsk-knowledge"
        namespace = "minsk"

        response = run_agent(user_message)

        # response = get_answer_from_document(
        #     user_message, index_name, namespace)

        bot_token = TELEGRAM_BOT_TOKEN
        send_message(chat_id, response, bot_token)
        send_slack_message(user_first_name, index_name, user_message)

    return '', 200
