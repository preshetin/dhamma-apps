from .schedule import schedule_bp


def register_api(app):
    app.register_blueprint(schedule_bp)
