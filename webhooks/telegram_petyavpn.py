import requests
import os
from flask import Blueprint, request

from utils.shared_functions import send_slack_message
from utils.supabase_client import create_chat, add_message
import json

telegram_petyavpn_bp = Blueprint('telegram_petyavpn', __name__)

TELEGRAM_BOT_TOKEN_PETYAVPN = os.environ.get('TELEGRAM_BOT_TOKEN_PETYAVPN')
API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN_PETYAVPN}'

def send_message(chat_id, text, parse_mode='html'):
    url = f'{API_URL}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    requests.post(url, json=payload)

def send_invoice(chat_id, amount):
    url = f'{API_URL}/sendInvoice'
    payload = {
        'chat_id': chat_id,
        'title': 'Один месяц VPN',
        'description': 'Использование VPN в течение одного месяца',
        'payload': 'stars_payment',
        'currency': 'XTR',
        'prices': [{'label': f"{amount} Stars", 'amount': amount}],
        'need_name': False,
        'need_phone_number': False,
        'need_email': False,
        'need_shipping_address': False,
    }
    requests.post(url, json=payload)

@telegram_petyavpn_bp.route('/webhook-petyavpn', methods=['POST'])
def webhook_petyavpn():
    update = request.get_json()
    send_slack_message('some_user', 'foo', json.dumps(update))

    # return '', 200
    
    # Handle callback query
    if 'callback_query' in update:
        callback_query = update['callback_query']
        chat_id = callback_query['message']['chat']['id']

        if callback_query['data'] == 'confirm_stars_purchase':
            amount = 100
            send_invoice(chat_id, amount)
            # TODO: db: add message from 'user' with text "confirm_stars_purchase"
        
        if callback_query['data'] == 'pay_button_clicked':
            url = f'{API_URL}/sendMessage'
            payload = {
                'chat_id': chat_id,
                'text': "Оплата VPN производится через покупку звезды телеграм. \n\n Чтобы купить звезды, перейдите в @PremiumBot. \n\nМесяц VPN составляет <b>100 звезд</b> (~180₽, точная сумма зависит от курса рубля и комиссии Telegram)  \n\nКак пополните баланс, возвращайтесь сюда",
                'parse_mode': 'html',
                'reply_markup': {
                    'inline_keyboard': [[{
                        'text': 'Я купил(a) звезды',
                        'callback_data': 'confirm_stars_purchase'
                    }]]
                }
            }
            requests.post(url, json=payload)
            # TODO: db: add message from 'bot' with text payload.text
            
            return '', 200

        if callback_query['data'] == 'free_connection':
            send_message(chat_id, "Вот инструкция и ваш ключ (В разработке. Пока пишите Пете @preshetin)", parse_mode='html')
            # TODO: panel_api: create new client in 3x-ui panel, set end_at to 7 days from now
            # TODO: db: add new message from 'bot' with text "free_connection instruction and key" 

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
            send_message(chat_id, f"Спасибо за оплату, {user_first_name} {user_last_name} (@{user_username})! \n\nVPN активирован на месяц. \n\nЕсли есть вопросы, напиши Пете @preshetin")
            # TODO: db: add one month to subscription end_at date
            # TODO: db: add message from 'user' with text "successful_payment"
            # TODO: db add new payment with amount 100 stars and chat_id
            # TODO: panel_api: activate client in 3x-ui panel, set end_at to 30 days from now
            return '', 200
           
        # Handle regular message
        user_message = update['message']['text']

        if user_message == '/start':
            # Create chat record in Supabase
            create_chat(
                chat_id=chat_id,
                username=user_username,
                first_name=user_first_name,
                last_name=user_last_name
            )
            
            # Add message to Supabase
            add_message(
                chat_id=chat_id,
                is_bot=False,
                text="/start",
                update_obj=update
            )

            url = f'{API_URL}/sendMessage'
            payload = {
                'chat_id': chat_id,
                'text': "Привет! 👋",
                'parse_mode': 'html',
                'reply_markup': {
                    'inline_keyboard': [[{
                        'text': 'Подключиться бесплатно',
                        'callback_data': 'free_connection'
                    }]]
                }
            }
            response = requests.post(url, json=payload)
            
            # Add bot's response to messages
            if response.ok:
                add_message(
                    chat_id=chat_id,
                    is_bot=True,
                    text=payload['text'],
                    update_obj=response.json()
                )
        elif user_message.lower() == 'оплата':
            send_invoice(chat_id, 100)
            send_message(chat_id, "Если у вас не получается оплатить (в РФ не работает ApplePay), попробуйте купить звезды через @PremiumBot и вернитесь сюда и нажмите кнопку оплаты.", parse_mode='html')
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
            # TODO: db: add message from 'bot' with text formatted_text

    return '', 200
