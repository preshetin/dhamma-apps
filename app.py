import time
import uuid
from dotenv import load_dotenv
from flask import Flask, jsonify
import os

from api import register_api
from webhooks import register_webhooks
from utils.panel_client import PanelClient


app = Flask(__name__)

if os.getenv('FLASK_ENV') == 'development':
    load_dotenv()

register_api(app)
register_webhooks(app)

# Initialize panel client
panel_client = PanelClient(
    base_url=os.environ.get('PANEL_BASE_URL'),
    username=os.environ.get('PANEL_USERNAME'),
    password=os.environ.get('PANEL_PASSWORD')
)

@app.route('/')
def get_inbounds():
    try:
        # return 'all good, connection string is working'
        # Example: add a client and return connection string
        chat_id = 1111
        expiry_time = (int(time.time()) + 7 * 24 * 60 * 60) * 1000
        client_id = str(uuid.uuid4())
        print('hey')
        conn_str = panel_client.add_client(email=f"{chat_id}", expiry_time=expiry_time, client_id=client_id   )
        return jsonify({"connection_string": conn_str})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Is My Car Okay Bot
# SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')
# OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

if __name__ == '__main__':
    app.run(debug=True)
