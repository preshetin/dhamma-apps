# api/schedule.py
from flask import Blueprint, jsonify, request

from utils.schedule_service import get_schedule_service

schedule_bp = Blueprint('schedule', __name__)

# /api/schedule?course_type=children&year=current


@schedule_bp.route('/api/schedule', methods=['GET'])
# TODO: make it /api/schedule
def get_schedule():
    location = request.args.get('location', default='all')
    status = request.args.get('status', default='open')
    year = request.args.get('year', default='current')
    course_type = request.args.get('course_type', default='ten-day')

    result = get_schedule_service(status, course_type, location, year)

    return jsonify(result)
