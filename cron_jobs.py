import os
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from utils.shared_functions import send_slack_message

if os.getenv('FLASK_ENV') == 'development':
    load_dotenv()

def cron_hello():
    print('cron_hello called')
    send_slack_message("cron", "system", "hello")

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(cron_hello, 'interval', minutes=1)
    print("Starting scheduler...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass