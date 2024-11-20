from flask import Flask, jsonify, request
import requests
import os
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def hello_fly():
    return 'hello world'

@app.route('/api/courses', methods=['GET'])
def get_courses():
    url = "https://www.dhamma.org/ru/schedules/schdullabha"
    response = requests.get(url)
    
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch the page"}), 500
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Use the query selector to find the table body
    table_body = soup.select_one("body > div > div > div:nth-child(8) > div:nth-child(6) > table:nth-child(4) > tbody")
    
    if not table_body:
        return jsonify({"error": "Failed to find the courses table"}), 500
    
    courses = []
    
    # Iterate over all tr elements except the first one (header)
    for tr in table_body.find_all('tr')[1:]:
        tds = tr.find_all('td')

        link = tds[0].find('a', text='Анкета*')
        if link:
            url = link.get('href')
        else:
          url = None
        
        if len(tds) < 6:
            continue

        print(tds[5])
        
        course = {
            "application_url": url,
            "date": tds[1].get_text(strip=True),
            "type": tds[2].get_text(strip=True),
            "status": tds[3].get_text(strip=True),
            "location": tds[4].get_text(strip=True),
            "description": tds[5].get_text(strip=True),
        }
        
        courses.append(course)
    
    return jsonify(courses)

# Replace with your actual tokens

# Is My Car Okay Bot
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

@app.route('/webhook', methods=['POST'])
def webhook():
    print(111)
    update = request.get_json()
    print(update)
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        user_message = update['message']['text']
        
        # Get response from OpenAI
        gpt_response = get_gpt_response(user_message)
        
        # Send response back to Telegram
        send_message(chat_id, gpt_response)
    
    return '', 200

def get_gpt_response(user_message):
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        'model': 'gpt-3.5-turbo',  # or any other model you want to use
        'messages': [{'role': 'user', 'content': user_message}],
    }
    
    response = requests.post(OPENAI_API_URL, headers=headers, json=data)
    response_json = response.json()
    
    # Extract the assistant's reply
    if 'choices' in response_json and len(response_json['choices']) > 0:
        return response_json['choices'][0]['message']['content']
    else:
        return "Sorry, I couldn't get a response from the AI."

def send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'  # Optional: use Markdown formatting
    }
    requests.post(url, json=payload)

if __name__ == '__main__':
    app.run(debug=True)