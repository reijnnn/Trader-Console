from flask          import render_template, redirect, url_for, flash, request, Blueprint, current_app
from flask_login    import login_required
from flask_wtf.csrf import CSRFError

from ..user.decorators  import *
from ..utils.pagination import Pagination

from collections import deque
from os          import path

frontend_bp = Blueprint('frontend', __name__, template_folder='templates')

@frontend_bp.route('/')
@login_required
def index():
	return render_template('index.html')

@frontend_bp.app_errorhandler(404)
def page_not_found(e):
	return redirect(url_for('frontend.index'))

@frontend_bp.app_errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400

@frontend_bp.route('/logs/', defaults={'type': 'info', 'page': 1})
@frontend_bp.route('/logs/<type>', defaults={'page': 1})
@frontend_bp.route('/logs/<type>/<int:page>')
@login_required
@is_super_admin
def logs(type, page):
	search     = request.args.get('search')
	cnt_rows   = 0
	logs_type  = type.lower()

	if logs_type == 'debug':
		log_file_path = current_app.config['APP_LOG_DEBUG_FILE']
	elif logs_type == 'error':
		log_file_path = current_app.config['APP_LOG_ERROR_FILE']
	else:
		log_file_path = current_app.config['APP_LOG_INFO_FILE']
		logs_type = 'info'

	if path.exists(log_file_path):
		with open(log_file_path, "r") as f:
			while True:
				line = f.readline()
				if not line:
					break

				if search:
					if line.lower().find(search.lower()) != -1:
						cnt_rows = cnt_rows + 1
				else:
					cnt_rows = cnt_rows + 1

	logs    = deque()
	num_row = 0
	if cnt_rows > 0 and path.exists(log_file_path):
		with open(log_file_path, "r") as f:
			while True:
				line = f.readline()
				if not line:
					break

				if search:
					if line.lower().find(search.lower()) != -1:
						logs.append(line)
						num_row = num_row + 1
				else:
					logs.append(line)
					num_row = num_row + 1

				if len(logs) > current_app.config['PAGINATION_PAGE_SIZE']:
					logs.popleft()

				if cnt_rows - num_row <= (page - 1) * current_app.config['PAGINATION_PAGE_SIZE']:
					break

	logs.reverse()

	pagination = Pagination(page=page,
							per_page=current_app.config['PAGINATION_PAGE_SIZE'],
							total_count=cnt_rows,
							filter_text=search)

	return render_template('logs.html', logs=logs, pagination=pagination, logs_type=logs_type)
