from dotenv import load_dotenv
from flask import Flask
import os

from api import register_api
from webhooks import register_webhooks


app = Flask(__name__)

if os.getenv('FLASK_ENV') == 'development':
    load_dotenv()

register_api(app)
register_webhooks(app)


@app.route('/')
def hello_fly():
    return 'hello world'


# Is My Car Okay Bot
# SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')
# OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

if __name__ == '__main__':
    app.run(debug=True)
