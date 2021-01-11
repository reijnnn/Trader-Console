from flask import render_template, flash, request, Blueprint, current_app, jsonify
from flask_login import login_required
from sqlalchemy import desc, or_
from ..extensions import db, logger
from ..user.decorators import *
from ..user.users_service import get_user_by_id, get_user_by_telegram_id, check_user_permission
from ..telegram_bot.notifications_service import add_notification
from ..utils.pagination import Pagination
from ..trader_bot.strategies import (
    Alert,
    Price,
    Volume,
    Envelope,
    DumpPriceHistory,
    StrategyType,
)
from .models import Tasks, TaskStatus
from .tasks_service import get_task, cancel_task
from .task import Task
from .forms import ModifyTaskForm
from json import loads

task_bp = Blueprint('task', __name__, template_folder='templates')


@task_bp.route('/monitor_tasks/', defaults={'page': 1})
@task_bp.route('/monitor_tasks/<int:page>')
@login_required
def monitor_tasks(page):
    query = db.session.query(Tasks)

    search = request.args.get('search')
    if search:
        search = '%' + search + '%'
        query = query.filter(or_(Tasks.task_status.ilike(search),
                                 Tasks.task_params.ilike(search),
                                 Tasks.task_name.ilike(search),
                                 Tasks.chat_id.ilike(search)))

    if not current_user.is_super_admin:
        if current_user.telegram_id:
            query = query.filter(Tasks.chat_id == current_user.telegram_id)
        else:
            query = query.filter(1 == 0)

    total_count = query.count()

    query = query.order_by(desc(Tasks.task_status == TaskStatus.ACTIVE), desc(Tasks.task_date), desc(Tasks.task_id)). \
        offset((page - 1) * current_app.config['PAGINATION_PAGE_SIZE']). \
        limit(current_app.config['PAGINATION_PAGE_SIZE'])
    tasks = query.all()

    pagination = Pagination(page=page,
                            per_page=current_app.config['PAGINATION_PAGE_SIZE'],
                            total_count=total_count,
                            filter_text=search)

    form = ModifyTaskForm(request.form)

    return render_template('tasks.html', tasks=tasks, pagination=pagination,
                           strategy_type_list=StrategyType.get_strategy_type_list(),
                           form=form)


@task_bp.route('/create_task', methods=['POST'])
@login_required
def create_task():
    form = ModifyTaskForm(request.form)

    if form.validate_on_submit():
        create_cmd = "/task create"
        param_suffix = '(required)'

        task_params = loads(form.task_params.data)
        for param in task_params:
            if param.endswith(param_suffix):
                strip_param = param[:-len(param_suffix)]
            else:
                strip_param = param

            create_cmd += " {}={}".format(strip_param, task_params[param])

        user = get_user_by_id(int(form.user.data))

        if not check_user_permission(user):
            flash("You don't have permission to work with this user", 'info')
            return redirect(url_for('task.monitor_tasks'))

        if user.telegram_id:
            logger.debug(create_cmd)
            Task(create_cmd, chat_id=user.telegram_id, from_ui=True)
        else:
            flash('User "{}" does not have telegram_id'.format(user.login), 'warning')

    return redirect(url_for('task.monitor_tasks'))


@task_bp.route('/edit_task', methods=['POST'])
@login_required
def edit_task():
    form = ModifyTaskForm(request.form)

    if form.validate_on_submit():
        param_suffix = '(required)'
        edit_cmd = "/task edit id={}".format(form.task_id.data)

        task_params = loads(form.task_params.data)
        for param in task_params:
            if param.endswith(param_suffix):
                strip_param = param[:-len(param_suffix)]
            else:
                strip_param = param

            edit_cmd += " {}={}".format(strip_param, task_params[param])

        user = get_user_by_id(int(form.user.data))

        if not check_user_permission(user):
            flash("You don't have permission to work with this user", 'info')
            return redirect(url_for('task.monitor_tasks'))

        if user.telegram_id:
            logger.debug(edit_cmd)
            Task(edit_cmd, chat_id=user.telegram_id, from_ui=True)
        else:
            flash('User "{}" does not have telegram_id'.format(user.login), 'warning')

    return redirect(url_for('task.monitor_tasks'))


@task_bp.route('/get_config_task', methods=['GET'])
@login_required
def get_config_task():
    task_name = request.args.get('task_name')
    task_id = int(request.args.get('task_id', -1))
    task_config = {}

    if task_id > 0:
        task = get_task(task_id)
        user = get_user_by_telegram_id(task.chat_id)

        if not check_user_permission(user):
            return jsonify(task_config)

        task_config = {
            'params': loads(task.task_params),
            'user_id': user.id
        }
        return jsonify(task_config)

    if task_name == StrategyType.ALERT:
        task_config = Alert.get_config()
    elif task_name == StrategyType.DUMP_PRICE_HISTORY:
        task_config = DumpPriceHistory.get_config()
    elif task_name == StrategyType.ENVELOPE:
        task_config = Envelope.get_config()
    elif task_name == StrategyType.PRICE:
        task_config = Price.get_config()
    elif task_name == StrategyType.VOLUME:
        task_config = Volume.get_config()

    task_config['user_id'] = current_user.id

    return jsonify(task_config)


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
        add_notification(text='Your task with id={} was canceled by admin'.format(task.task_id),
                         chat_id=task.chat_id,
                         task_id=task.task_id,
                         reply_to_message_id=task.reply_to_message_id)

    flash("Task with id={} successfully canceled".format(task_id), 'success')

    return redirect(url_for('task.monitor_tasks'))
