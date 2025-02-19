
import requests
import os
from flask import Blueprint, request

telegram_petyavpn_bp = Blueprint('telegram_petyavpn', __name__)


TELEGRAM_BOT_TOKEN_PETYAVPN = os.environ.get(
    'TELEGRAM_BOT_TOKEN_PETYAVPN')


@telegram_petyavpn_bp.route('/webhook-petyavpn', methods=['POST'])
def webhook_petyavpn():
    update = request.get_json()
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        user_message = update['message']['text']
        user_info = update['message']['from']
        user_first_name = user_info.get('first_name', '')
        user_last_name = user_info.get('last_name', '')
        user_username = user_info.get('username', '')

        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

        # formatted_text = telegram_format(text)
        formatted_text = user_message

        payload = {
            'chat_id': chat_id,
            'text': formatted_text,
            'parse_mode': 'html'
        }
        requests.post(url, json=payload)

        # if user_username != 'preshetin':
        #     send_slack_message(user_username, index_name, user_message)

    return '', 200
