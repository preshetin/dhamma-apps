import time
import uuid
import requests
import os
from flask import Blueprint, request

from utils.panel_client import PanelClient
from utils.shared_functions import send_slack_message
from utils.supabase_client import create_chat, add_message, create_subscription,create_payment
import json

telegram_petyavpn_bp = Blueprint('telegram_petyavpn', __name__)


panel_client = PanelClient(
    base_url=os.environ.get('PANEL_BASE_URL'),
    username=os.environ.get('PANEL_USERNAME'),
    password=os.environ.get('PANEL_PASSWORD')
)

TELEGRAM_BOT_TOKEN_PETYAVPN = os.environ.get('TELEGRAM_BOT_TOKEN_PETYAVPN')
API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN_PETYAVPN}'

VPN_MONTHLY_AMOUNT = 3  # Amount in stars for one month of VPN

def send_message(chat_id, text, parse_mode='html'):
    url = f'{API_URL}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    requests.post(url, json=payload)

def send_invoice(chat_id, amount=VPN_MONTHLY_AMOUNT, payload_data=None):
    url = f'{API_URL}/sendInvoice'
    payload = {
        'chat_id': chat_id,
        'title': 'Один месяц VPN',
        'description': 'Использование VPN в течение одного месяца',
        'payload': json.dumps(payload_data) if payload_data else 'stars_payment',
        'currency': 'XTR',
        'prices': [{'label': f"{amount} Stars", 'amount': amount}],
        'need_name': False,
        'need_phone_number': False,
        'need_email': False,
        'need_shipping_address': False,
    }
    requests.post(url, json=payload)

def load_free_connection_message():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    msg_path = os.path.join(base_dir, "free_connection_message.txt")
    with open(msg_path, encoding="utf-8") as f:
        return f.read()

def get_username(update):
    if 'message' in update and 'from' in update['message']:
        return update['message']['from'].get('username', '')
    elif 'callback_query' in update and 'from' in update['callback_query']:
        return update['callback_query']['from'].get('username', '')
    return ''

@telegram_petyavpn_bp.route('/webhook-petyavpn', methods=['POST'])
def webhook_petyavpn():
    update = request.get_json()
    user_username = get_username(update)
    send_slack_message(user_username, 'foo 2', json.dumps(update))

    # return '', 200
    
    # Handle callback query
    if 'callback_query' in update:
        callback_query = update['callback_query']
        chat_id = callback_query['message']['chat']['id']

        if callback_query['data'] == 'free_connection':
            free_msg = load_free_connection_message()
            send_message(chat_id, free_msg, parse_mode='html')
            # call add_client and get connection string

            expiry_time = (int(time.time()) + 7 * 24 * 60 * 60) * 1000

            client_id = str(uuid.uuid4())

            email  = f"{chat_id}-{user_username}"

            connection_string = panel_client.add_client(email=email, expiry_time=expiry_time, client_id=client_id   )

            send_message(chat_id, f"Ваш бесплатный VPN активирован на 7 дней! \n\n Вот ваша ссылка для подключения: \n\n<code>{connection_string}</code> \n\n Если есть вопросы, напишите Пете @preshetin", parse_mode='html')

            create_subscription(
                chat_id=chat_id,
                panel_client_id=client_id,
                email=email,
                url=connection_string,
                is_active=True,
                expity_time=expiry_time,
            )

            # TODO: panel_api: create new client in 3x-ui panel, set end_at to 7 days from now
            # TODO: db: add new message from 'bot' with text "free_connection instruction and key" 

    # Handle pre_checkout_query
    if 'pre_checkout_query' in update:
        pre_checkout_query = update['pre_checkout_query']
        pre_checkout_query_id = pre_checkout_query['id']
        invoice_payload = pre_checkout_query.get('invoice_payload', '')
        client_id = None
        try:
            payload_data = json.loads(invoice_payload)
            client_id = payload_data.get('client_id')
        except Exception:
            client_id = None

        # Check client_id presence and validity
        client = None
        if client_id:
            client = panel_client.get_client_by_id(client_id)

        if not client_id or not client:
            # Respond with ok: False and error message
            url = f'{API_URL}/answerPreCheckoutQuery'
            payload = {
                'pre_checkout_query_id': pre_checkout_query_id,
                'ok': False,
                'error_message': 'Не удалось обработать оплату. Пожалуйста, попробуйте позже или обратитесь к @preshetin.'
            }
            requests.post(url, json=payload)
            send_slack_message(
                get_username(update),
                "Error: client_id not found or invalid in pre_checkout_query payload",
                json.dumps(update)
            )
            return '', 200

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
            payment_info = update['message']['successful_payment']
            invoice_payload = payment_info.get('invoice_payload', '')
            chat_id = update['message']['chat']['id']
            user_info = update['message']['from']
            user_first_name = user_info.get('first_name', '')
            user_last_name = user_info.get('last_name', '')
            user_username = user_info.get('username', '')
            amount = payment_info.get('total_amount', VPN_MONTHLY_AMOUNT)
            currency = payment_info.get('currency', 'XTR')
            transaction_id = payment_info.get('telegram_payment_charge_id', '')
            comment = ''
            client_id = None
            # Try to extract client_id from payload
            try:
                payload_data = json.loads(invoice_payload)
                client_id = payload_data.get('client_id')
            except Exception:
                pass
            if not client_id:
                # If client_id is not present, do not try to extend time or create a new client
                send_message(chat_id, f"Ошибка: не удалось определить клиента для продления VPN. Пожалуйста, обратитесь к @preshetin")
                send_slack_message(user_username, "Error: client_id not found in payment payload", json.dumps(update))
                return '', 200
            client = panel_client.get_client_by_id(client_id)
            if not client:
                # If client is not found, do not proceed
                send_message(chat_id, f"Ошибка: не удалось найти клиента для продления VPN. Пожалуйста, обратитесь к @preshetin")
                send_slack_message(user_username, "Error: client not found", json.dumps(update))
                return '', 200
            # Calculate new expiry time
            now_ms = int(time.time() * 1000)
            old_expiry = client.get('expiryTime', 0)
            if old_expiry < now_ms:
                new_expiry = now_ms + 30 * 24 * 60 * 60 * 1000
            else:
                new_expiry = old_expiry + 30 * 24 * 60 * 60 * 1000
            client['expiryTime'] = new_expiry
            panel_client.update_client(client['id'], client)
            # Notify user
            new_expiry_date = time.strftime('%d.%m.%Y', time.localtime(new_expiry / 1000))
            send_message(chat_id, f"Спасибо за оплату, {user_first_name} {user_last_name} (@{user_username})!\n\nVPN активирован до {new_expiry_date}.\n\nЕсли есть вопросы, напиши Пете @preshetin")

            comment = f"Payment from old expiry date {time.strftime('%d.%m.%Y', time.localtime(old_expiry / 1000))} to new expiry {new_expiry_date}"
            create_payment(
                chat_id=chat_id,
                amount=amount,
                currency_code=currency,
                comment=comment,
                transaction_id=transaction_id
            )
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
            'text': "Привет! 👋 Это VPN от Пети @preshetin. \n\n 7 дней бесплатно \n\n Далее 100 звезд Телеграм (~170 ₽) в месяц",
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
            send_invoice(chat_id, VPN_MONTHLY_AMOUNT)
            send_message(chat_id, "Если у вас не получается оплатить (в РФ не работает ApplePay), попробуйте купить звезды через @PremiumBot и вернитесь сюда и нажмите кнопку оплаты.", parse_mode='html')
            send_slack_message(user_username, 'todo: remove this', json.dumps(update))
        else:
            formatted_text = "Привет! 👋\n\nЧтобы подключиться к VPN, отправьте мне /start.\n\nЕсли у вас есть вопросы, напишите Пете @preshetin" 
            send_message(chat_id, formatted_text, parse_mode='html')

    return '', 200
