# api/schedule.py
from flask import Blueprint, jsonify, request
import requests
from bs4 import BeautifulSoup

schedule_bp = Blueprint('schedule', __name__)


@schedule_bp.route('/api/courses', methods=['GET'])
# TODO: make it /api/schedule
def get_schedule():
    url = "https://www.dhamma.org/ru/schedules/schdullabha"
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch the page"}), 500

    soup = BeautifulSoup(response.content, 'html.parser')

    courses_groups = [
        {
            # first table, dullabha current year
            "title": "2024 Десятидневные и другие курсы для взрослых",
            "block": "dullabha",
            "year": "current",
            "dom_element": "body > div > div > div:nth-child(8) > div:nth-child(2) > table:nth-child(4) > tbody",
        },
        {
            # second table, dullabha next year
            "title": "2025 Десятидневные и другие курсы для взрослых",
            "block": "dullabha",
            "year": "next",
            "dom_element": "body > div > div > div:nth-child(8) > div:nth-child(2) > table:nth-child(6) > tbody",
        },
        # Separator: Курсы вне центров
        {
            # 3-rd table: ten days, childern, one day,
            # location: russia
            # current year
            "title": "2024 Курсы медитации в России",
            "block": "russia",
            "year": "current",
            "dom_element": "body > div > div > div:nth-child(8) > div:nth-child(4) > table:nth-child(4) > tbody",
        },
        {
            # 4-rd table, russia, next year
            "title": "2025 Курсы медитации в России",
            "block": "russia",
            "year": "next",
            "dom_element": "body > div > div > div:nth-child(8) > div:nth-child(4) > table:nth-child(6) > tbody",
        },
        {
            # 5th table, spb current year
            "title": "2024 Санкт-Петербург Курсы",
            "block": "spb",
            "year": "current",
            "dom_element": "body > div > div > div:nth-child(8) > div:nth-child(4) > table:nth-child(8) > tbody",
        },
        {
            # 6th table, spb next year
            "title": "2025 Санкт-Петербург Курсы",
            "block": "spb",
            "year": "next",
            "dom_element": "body > div > div > div:nth-child(8) > div:nth-child(4) > table:nth-child(10) > tbody",
        },
        {
            # 7th table, ekt current year
            "title": "2024 Екатеринбург Курсы",
            "block": "ekt",
            "year": "current",
            "dom_element": "body > div > div > div:nth-child(8) > div:nth-child(4) > table:nth-child(12) > tbody",
        },
        {
            # 8th table, ekt next year
            "title": "2025 Екатеринбург Курсы",
            "block": "ekt",
            "year": "next",
            "dom_element": "body > div > div > div:nth-child(8) > div:nth-child(4) > table:nth-child(14) > tbody",
        },
        # Separator: Курсы для подростков и детей
        {
            # 9th table,
            "title": "2024 Курсы для подростков и детей",
            "block": "childen",
            "year": "current",
            "dom_element": "body > div > div > div:nth-child(8) > div:nth-child(6) > table:nth-child(4) > tbody",
        },
        {
            # 10th table, childent next year
            "title": "2025 Курсы для подростков и детей",
            "block": "childen",
            "year": "next",
            "dom_element": "body > div > div > div:nth-child(8) > div:nth-child(6) > table:nth-child(6) > tbody",
        },
    ]

    # Use the query selector to find the table body
    table_body = soup.select_one(
        "body > div > div > div:nth-child(8) > div:nth-child(6) > table:nth-child(4) > tbody")

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
