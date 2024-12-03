import requests
from bs4 import BeautifulSoup


def get_schedule_service(status, course_type='ten-day', location='all', year='current'):
    url = "https://www.dhamma.org/ru/schedules/schdullabha"
    response = requests.get(url)

    if response.status_code != 200:
        raise 'Failed to fetch the page'

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
            "block": "children",
            "year": "current",
            "dom_element": "body > div > div > div:nth-child(8) > div:nth-child(6) > table:nth-child(4) > tbody",
        },
        {
            # 10th table, childent next year
            "title": "2025 Курсы для подростков и детей",
            "block": "children",
            "year": "next",
            "dom_element": "body > div > div > div:nth-child(8) > div:nth-child(6) > table:nth-child(6) > tbody",
        },
    ]

    content = response.content
    soup = BeautifulSoup(content, features='html.parser')

    courses = []

    for courses_group in courses_groups:
        courses_block = build_courses_list_from_table(
            soup, courses_group)
        for course in courses_block:
            courses.append(course)

    result = courses

    if course_type == 'children':
        result = list(filter(lambda d: d['block'] == 'children', courses))
        return result

    if status == 'open':
        result = list(filter(lambda d: d['application_url'] != None, courses))
        return result

    return result


def build_courses_list_from_table(soup, course_group):

    table_body = soup.select_one(
        course_group['dom_element'])

    if not table_body:
        raise "Failed to find the courses table"
        # return jsonify({"error": "Failed to find the courses table"}), 500

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
            "block": course_group['block'],
            "year": course_group['year']
        }

        courses.append(course)

    return courses
