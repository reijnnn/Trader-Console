from flask import render_template, flash, request, Blueprint, current_app
from flask_login import login_required
from sqlalchemy import desc, or_
from ..extensions import db, proxy_bot, logger
from ..user.decorators import *
from ..utils.pagination import Pagination
from .models import Proxies

proxy_bot_bp = Blueprint('proxy_bot', __name__, template_folder='templates')


@proxy_bot_bp.route('/monitor_proxy_bot/', defaults={'page': 1})
@proxy_bot_bp.route('/monitor_proxy_bot/<int:page>')
@login_required
@is_super_admin
def monitor_proxy_bot(page):
    query = db.session.query(Proxies)

    search = request.args.get('search')
    if search:
        search = '%' + search + '%'
        query = query.filter(or_(Proxies.proxy_type.ilike(search),
                                 Proxies.proxy_ip.ilike(search)))

    total_count = query.count()

    query = query.order_by(desc(Proxies.proxy_weight), desc(Proxies.proxy_good_try)). \
        offset((page - 1) * current_app.config['PAGINATION_PAGE_SIZE']). \
        limit(current_app.config['PAGINATION_PAGE_SIZE'])
    proxies = query.all()

    pagination = Pagination(page=page,
                            per_page=current_app.config['PAGINATION_PAGE_SIZE'],
                            total_count=total_count,
                            filter_text=search)

    return render_template('proxy_bot.html',
                           proxies=proxies,
                           pagination=pagination,
                           status=proxy_bot.get_status(),
                           thread_status=proxy_bot.get_thread_status(),
                           active_proxy_id=proxy_bot.get_active_proxy_id())


@proxy_bot_bp.route('/add_proxy', methods=['POST'])
@login_required
@is_super_admin
def add_proxy():
    if request.method == 'POST':

        proxy_str = request.form.get('proxy_list')

        if not proxy_str:
            return redirect(url_for('proxy_bot.monitor_proxy_bot'))

        proxy_str = proxy_str.rstrip(';')

        proxy_list = proxy_str.split(';')
        proxy_list = [proxy.strip(' ').lower() for proxy in proxy_list]

        for proxy in proxy_list:
            type_ip_port = proxy.split(':')
            if len(type_ip_port) != 3:
                flash('Proxy "{}" format is incorrect. Expected format is "type:ip:port"'.format(proxy), 'danger')
                return redirect(url_for('proxy_bot.monitor_proxy_bot'))

            if type_ip_port[0] not in ['http', 'https']:
                flash('Proxy type "{}" is incorrect. Expected "http" or "https"'.format(type_ip_port[0]), 'danger')
                return redirect(url_for('proxy_bot.monitor_proxy_bot'))

        exists_proxy_list = []
        new_proxy_list = []
        for proxy in proxy_list:
            type_ip_port = proxy.split(':')

            exist_proxy = db.session.query(Proxies).filter_by(proxy_ip=type_ip_port[1],
                                                              proxy_port=type_ip_port[2]).count()
            if exist_proxy:
                exists_proxy_list.append(proxy)
            else:
                new_proxy_list.append(proxy)

                new_proxy = Proxies(
                    proxy_type=type_ip_port[0],
                    proxy_ip=type_ip_port[1],
                    proxy_port=type_ip_port[2]
                )
                db.session.add(new_proxy)
                db.session.commit()

                logger.debug(new_proxy)

        if len(exists_proxy_list):
            flash(
                "{} proxy server/servers already exist: {}".format(len(exists_proxy_list), " ".join(exists_proxy_list)),
                'warning')
        if len(new_proxy_list):
            flash("{} proxy server/servers successfully added".format(len(new_proxy_list)), 'success')

    return redirect(url_for('proxy_bot.monitor_proxy_bot'))


@proxy_bot_bp.route('/delete_proxy/<proxy_id>')
@login_required
@is_super_admin
def delete_proxy(proxy_id):
    proxy = db.session.query(Proxies).filter_by(proxy_id=proxy_id).first()
    if not proxy:
        flash("Proxy not found", 'info')
        return redirect(url_for('proxy_bot.monitor_proxy_bot'))

    db.session.delete(proxy)
    db.session.commit()

    flash('Proxy "{}:{}" successfully deleted'.format(proxy.proxy_ip, proxy.proxy_port), 'success')

    return redirect(url_for('proxy_bot.monitor_proxy_bot'))


@proxy_bot_bp.route('/start_proxy_bot')
@login_required
@is_super_admin
def start_proxy_bot():
    proxy_bot.restart()
    return redirect(url_for('proxy_bot.monitor_proxy_bot'))


@proxy_bot_bp.route('/stop_proxy_bot')
@login_required
@is_super_admin
def stop_proxy_bot():
    proxy_bot.cancel()
    return redirect(url_for('proxy_bot.monitor_proxy_bot'))
