from flask import render_template, redirect, url_for, flash, request, Blueprint, current_app
from flask_login import login_required

from sqlalchemy import desc, or_

from ..extensions         import login_manager, csrf, db
from ..user.decorators    import *
from ..telegram_bot.notifications_service import add_notification
from ..utils.pagination   import Pagination
from .models              import Tasks, Task_status
from .tasks_service       import get_task, cancel_task

task_bp = Blueprint('task', __name__, template_folder='templates')

@task_bp.route('/monitor_tasks/', defaults={'page': 1})
@task_bp.route('/monitor_tasks/<int:page>')
@login_required
def monitor_tasks(page):
	query = db.session.query(Tasks)

	search = request.args.get('search')
	if search:
		search = '%' + search + '%'
		query  = query.filter(or_(Tasks.task_status.ilike(search),
									Tasks.task_params.ilike(search),
									 Tasks.task_name.ilike(search),
									  Tasks.chat_id.ilike(search)))

	if not current_user.is_super_admin:
		if current_user.telegram_id:
			query = query.filter(Tasks.chat_id == current_user.telegram_id)
		else:
			query = query.filter(1 == 0)

	total_count = query.count()

	query = query.order_by(desc(Tasks.task_status == Task_status.ACTIVE), desc(Tasks.task_date), desc(Tasks.task_id)).\
					offset((page - 1) * current_app.config['PAGINATION_PAGE_SIZE']).\
					limit(current_app.config['PAGINATION_PAGE_SIZE'])
	tasks = query.all()

	pagination = Pagination(page=page,
							per_page=current_app.config['PAGINATION_PAGE_SIZE'],
							total_count=total_count,
							filter_text=search)

	return render_template('tasks.html', tasks=tasks, pagination=pagination)

@task_bp.route('/cancel_active_task/<task_id>')
@login_required
def cancel_active_task(task_id):
	task = get_task(task_id)
	if not task:
		flash("Task with id={} not found".format(task_id), 'info')
		return redirect(url_for('task.monitor_tasks'))

	if not current_user.is_super_admin and current_user.telegram_id != task.chat_id:
		flash("You don't have permission to cancel this task", 'info')
		return redirect(url_for('task.monitor_tasks'))

	cancel_task(task.task_id)
	if task.chat_id:
		add_notification(text=('Your task with id={} was canceled by admin').format(task.task_id),
						chat_id=task.chat_id,
						task_id=task.task_id,
						reply_to_message_id=task.reply_to_message_id)

	flash("Task with id={} successfully canceled".format(task_id), 'success')

	return redirect(url_for('task.monitor_tasks'))
