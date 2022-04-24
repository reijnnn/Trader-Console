from collections import deque
from os import path

from flask import render_template, request, Blueprint, current_app, flash
from flask_login import login_required
from flask_wtf.csrf import CSRFError

from ..user.decorators import *
from ..utils.pagination import Pagination

frontend_bp = Blueprint('frontend', __name__, template_folder='templates')


@frontend_bp.route('/')
@login_required
def index():
    return render_template('index.html')


@frontend_bp.app_errorhandler(404)
def handle_not_found(e):
    flash(str(e), 'warning')
    return redirect(url_for('frontend.index'))


@frontend_bp.app_errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400


@frontend_bp.route('/logs/', defaults={'level': 'info', 'page': 1})
@frontend_bp.route('/logs/<level>', defaults={'page': 1})
@frontend_bp.route('/logs/<level>/<int:page>')
@login_required
@is_super_admin
def logs(level, page):
    search = request.args.get('search')
    log_level = level.lower()

    if log_level == 'debug':
        log_file_path = current_app.config['APP_LOG_DEBUG_FILE']
    elif log_level == 'error':
        log_file_path = current_app.config['APP_LOG_ERROR_FILE']
    else:
        log_file_path = current_app.config['APP_LOG_INFO_FILE']
        log_level = 'info'

    cnt_rows = 0
    if path.exists(log_file_path):
        with open(log_file_path, "r") as f:
            for line in f:
                if not search or search and search.lower() in line.lower():
                    cnt_rows += 1

    logs_result = deque(maxlen=current_app.config['PAGINATION_PAGE_SIZE'])

    num_row = 0
    if cnt_rows > 0 and path.exists(log_file_path):
        with open(log_file_path, "r") as f:
            for line in f:
                if not search or search and search.lower() in line.lower():
                    logs_result.append(line)
                    num_row += 1

                if cnt_rows - num_row <= (page - 1) * current_app.config['PAGINATION_PAGE_SIZE']:
                    break

    logs_result.reverse()

    pagination = Pagination(page=page,
                            per_page=current_app.config['PAGINATION_PAGE_SIZE'],
                            total_count=cnt_rows,
                            filter_text=search)

    return render_template('logs.html', logs=logs_result, pagination=pagination, log_level=log_level)
