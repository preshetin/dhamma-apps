from flask import Flask, jsonify
import requests
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

if __name__ == '__main__':
    app.run(debug=True)