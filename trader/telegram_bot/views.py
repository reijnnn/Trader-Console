from flask import render_template, request, Blueprint, current_app
from flask_login import login_required
from sqlalchemy import desc, or_
from ..extensions import db, telegram_bot
from ..user.decorators import *
from ..utils.pagination import Pagination
from .models import Notifications

telegram_bot_bp = Blueprint('telegram_bot', __name__, template_folder='templates')


@telegram_bot_bp.route('/monitor_telegram_bot/', defaults={'page': 1})
@telegram_bot_bp.route('/monitor_telegram_bot/<int:page>')
@login_required
def monitor_telegram_bot(page):
    query = db.session.query(Notifications)

    search = request.args.get('search')
    if search:
        search = '%' + search + '%'
        query = query.filter(or_(Notifications.notif_text.ilike(search),
                                 Notifications.notif_status.ilike(search),
                                 Notifications.chat_id.ilike(search)))

    if not current_user.is_super_admin:
        if current_user.telegram_id:
            query = query.filter(Notifications.chat_id == current_user.telegram_id)
        else:
            query = query.filter(1 == 0)

    total_count = query.count()

    query = query.order_by(desc(Notifications.notif_date), desc(Notifications.notif_id)). \
        offset((page - 1) * current_app.config['PAGINATION_PAGE_SIZE']). \
        limit(current_app.config['PAGINATION_PAGE_SIZE'])
    notifications = query.all()

    pagination = Pagination(page=page,
                            per_page=current_app.config['PAGINATION_PAGE_SIZE'],
                            total_count=total_count,
                            filter_text=search)

    return render_template('telegram_bot.html',
                           notifications=notifications,
                           pagination=pagination,
                           bot_name=current_app.config['TELEGRAM_BOT_NAME'],
                           status=telegram_bot.get_status(),
                           thread_status=telegram_bot.get_thread_status())


@telegram_bot_bp.route('/start_telegram_bot')
@login_required
@is_super_admin
def start_telegram_bot():
    telegram_bot.restart()
    return redirect(url_for('telegram_bot.monitor_telegram_bot'))


@telegram_bot_bp.route('/stop_telegram_bot')
@login_required
@is_super_admin
def stop_telegram_bot():
    telegram_bot.cancel()
    return redirect(url_for('telegram_bot.monitor_telegram_bot'))
