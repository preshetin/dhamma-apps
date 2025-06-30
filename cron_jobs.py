import os
import time
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from utils.shared_functions import send_slack_message
from utils.panel_client import PanelClient
from webhooks.telegram_petyavpn import send_invoice, send_message, VPN_MONTHLY_AMOUNT

# load_dotenv()

if os.getenv('FLASK_ENV') == 'development':
    load_dotenv()

def cron_upcoming_payment_check():
    print('cron_upcoming_payment_check called')
    send_slack_message("cron_upcoming_payment_check", "system", "hello")
    panel_client = PanelClient(
        base_url=os.environ.get('PANEL_BASE_URL'),
        username=os.environ.get('PANEL_USERNAME'),
        password=os.environ.get('PANEL_PASSWORD')
    )
    now_ms = int(time.time() * 1000)
    one_day_ms = 24 * 60 * 60 * 1000
    clients = panel_client.get_clients()
    for client in clients:
        expiry_time = client.get('expiryTime', 0)
        if 0 < expiry_time - now_ms < one_day_ms:
            email = client.get('email', '')
            if '-' in email:
                chat_id = email.split('-')[0]
                try:
                    chat_id_int = int(chat_id)
                    send_message(chat_id_int, "⏰ Срок действия вашего VPN истекает в течение 24 часов. Пожалуйста, оплатите, чтобы продлить доступ.")
                    # Add client_id to payload for invoice
                    send_invoice(chat_id_int, amount=VPN_MONTHLY_AMOUNT, payload_data={"client_id": client.get("id")})
                    send_message(chat_id_int, "Если у вас не получается оплатить (в РФ не работает ApplePay), попробуйте купить звезды через @PremiumBot и вернитесь сюда и нажмите кнопку оплаты.", parse_mode='html')
                    
                    send_slack_message("cron_upcoming_payment_check", "system", f"Sent invoice to {chat_id_int} for client `{email}` with amount {VPN_MONTHLY_AMOUNT} XTR")
                except Exception as e:
                    print(f"Failed to send message to chat_id {chat_id}: {e}")

if __name__ == '__main__':
  # cron_upcoming_payment_check()
    scheduler = BlockingScheduler()
    scheduler.add_job(
      cron_upcoming_payment_check,
      'cron',
      hour=14,
      minute=42,
      timezone='Europe/Moscow'  # GMT+3
    )
    print("Starting scheduler...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass