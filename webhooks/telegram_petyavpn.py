import requests
import os
from flask import Blueprint, request

from utils.shared_functions import send_slack_message
import json

telegram_petyavpn_bp = Blueprint('telegram_petyavpn', __name__)

TELEGRAM_BOT_TOKEN_PETYAVPN = os.environ.get('TELEGRAM_BOT_TOKEN_PETYAVPN')
API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN_PETYAVPN}'

@telegram_petyavpn_bp.route('/webhook-petyavpn', methods=['POST'])
def webhook_petyavpn():
    update = request.get_json()
    send_slack_message('some_user', 'foo', json.dumps(update))
    
    # Handle callback query
    if 'callback_query' in update:
        callback_query = update['callback_query']
        chat_id = callback_query['message']['chat']['id']

        if callback_query['data'] == 'confirm_stars_purchase':
            # Send invoice
            url = f'{API_URL}/sendInvoice'
            payload = {
                'chat_id': chat_id,
                'title': 'VPN for June, 2025',
                'description': 'Purchase 100 Telegram Stars',
                'payload': 'stars_payment',
                'currency': 'XTR',
                'prices': [{'label': '100 Stars', 'amount': 100}],
                'need_name': False,
                'need_phone_number': False,
                'need_email': False,
                'need_shipping_address': False,
            }
            requests.post(url, json=payload)
        
        if callback_query['data'] == 'pay_button_clicked':
            url = f'{API_URL}/sendMessage'
            payload = {
                'chat_id': chat_id,
                'text': "Оплата VPN производится через покупку звезды телеграм. 🌟\n\n Чтобы купить звезды, перейдите в @PremiumBot. \n\n Месяц использования VPN составляет <b>100 звезд</b> ((~170₽, точная сумма зависит от курса рубля и комиссии Telegram))  \n\nКак пополните баланс, возвращайтесь сюда",
                'parse_mode': 'html',
                'reply_markup': {
                    'inline_keyboard': [[{
                        'text': 'Я купил(a) звезды',
                        'callback_data': 'confirm_stars_purchase'
                    }]]
                }
            }
            requests.post(url, json=payload)
            
            return '', 200

    # Handle pre_checkout_query
    if 'pre_checkout_query' in update:
        pre_checkout_query_id = update['pre_checkout_query']['id']
        url = f'{API_URL}/answerPreCheckoutQuery'
        payload = {
            'pre_checkout_query_id': pre_checkout_query_id,
            'ok': True
        }
        requests.post(url, json=payload)
        return '', 200

    if 'message' in update:
        chat_id = update['message']['chat']['id']
        user_info = update['message']['from']
        user_first_name = user_info.get('first_name', '')
        user_last_name = user_info.get('last_name', '')
        user_username = user_info.get('username', '')

        # Handle successful payment
        if 'successful_payment' in update['message']:
            url = f'{API_URL}/sendMessage'
            payload = {
                'chat_id': chat_id,
                'text': "Thank you for your payment! 🌟",
                'parse_mode': 'html'
            }
            requests.post(url, json=payload)
            return '', 200

        # Handle regular message
        user_message = update['message']['text']
        
        if user_message.lower() == 'оплата':
            # Send invoice
            url = f'{API_URL}/sendInvoice'
            payload = {
                'chat_id': chat_id,
                'title': 'VPN for June, 2025',
                'description': 'Purchase 100 Telegram Stars',
                'payload': 'stars_payment',
                # 'provider_token': os.environ.get('TELEGRAM_PAYMENT_TOKEN'),  # You need to set this in environment variables
                'currency': 'XTR',
                'prices': [{'label': '100 Stars', 'amount': 100}],  # Amount in cents (1 USD)
                'need_name': False,
                'need_phone_number': False,
                'need_email': False,
                'need_shipping_address': False,
            }
            requests.post(url, json=payload)
        else:
            # Regular message handling
            url = f'{API_URL}/sendMessage'
            formatted_text = user_message
            payload = {
                'chat_id': chat_id,
                'text': f"Я пока только уменю принимать оплату. \n\nЕсли есть вопрос, напиши Пете @preshetin",
                'parse_mode': 'html',
                'reply_markup': {
                    'inline_keyboard': [[{
                        'text': 'Оплатить',
                        'callback_data': 'pay_button_clicked'
                    }]]
                }
            }
            requests.post(url, json=payload)

    return '', 200
