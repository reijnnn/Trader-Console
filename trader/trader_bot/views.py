from flask import render_template, request, Blueprint, current_app
from flask_login import login_required
from sqlalchemy import desc, or_
from ..extensions import db, trader_bot
from ..user.decorators import *
from ..utils.pagination import Pagination
from .models import BinanceKlines

trader_bot_bp = Blueprint('trader_bot', __name__, template_folder='templates')


@trader_bot_bp.route('/monitor_trader_bot/', defaults={'page': 1})
@trader_bot_bp.route('/monitor_trader_bot/<int:page>')
@login_required
@is_admin
def monitor_trader_bot(page):
    query = db.session.query(BinanceKlines)

    search = request.args.get('search')
    if search:
        search = '%' + search + '%'
        query = query.filter(or_(BinanceKlines.symbol.ilike(search),
                                 BinanceKlines.interval.ilike(search),
                                 BinanceKlines.open_time.ilike(search)))

    total_count = query.count()

    query = query.order_by(desc(BinanceKlines.open_time)). \
        offset((page - 1) * current_app.config['PAGINATION_PAGE_SIZE']). \
        limit(current_app.config['PAGINATION_PAGE_SIZE'])
    klines = query.all()

    pagination = Pagination(page=page,
                            per_page=current_app.config['PAGINATION_PAGE_SIZE'],
                            total_count=total_count,
                            filter_text=search)

    return render_template('trader_bot.html',
                           klines=klines,
                           pagination=pagination,
                           status=trader_bot.get_status(),
                           thread_status=trader_bot.get_thread_status())


@trader_bot_bp.route('/start_trader_bot')
@login_required
@is_super_admin
def start_trader_bot():
    trader_bot.restart()
    return redirect(url_for('trader_bot.monitor_trader_bot'))


@trader_bot_bp.route('/stop_trader_bot')
@login_required
@is_super_admin
def stop_trader_bot():
    trader_bot.cancel()
    return redirect(url_for('trader_bot.monitor_trader_bot'))
