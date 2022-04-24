from datetime import datetime
from html import escape

from flask import current_app


def escape_text(msg):
    return escape(msg)


def wrap_code(msg):
    return '<code>{}</code>'.format(msg)


def unwrap_code(msg):
    return msg.replace('<code>', '').replace('</code>', '')


def time_now():
    return datetime.now().replace(microsecond=0)


def get_app_name():
    return current_app.config['APP_NAME']


def get_telegram_admin_username():
    return current_app.config['TELEGRAM_ADMIN_USERNAME']
