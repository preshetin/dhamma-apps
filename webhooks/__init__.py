from .telegram_petyavpn import telegram_petyavpn_bp
# from .telegram_children import telegram_children_bp
# from .telegram_dullabha import telegram_dullabha_bp
# from .telegram_minsk import telegram_minsk_bp


def register_webhooks(app):
    app.register_blueprint(telegram_petyavpn_bp)
    # app.register_blueprint(telegram_children_bp)
    # app.register_blueprint(telegram_dullabha_bp)
    # app.register_blueprint(telegram_minsk_bp)
