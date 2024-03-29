from flask import render_template, flash, request, Blueprint, current_app
from flask_login import login_user, logout_user, login_required
# noinspection PyPackageRequirements
from sqlalchemy import or_

from ..extensions import login_manager, logger, db
from ..telegram_bot.notifications_service import add_notification
from ..utils.pagination import Pagination
from .decorators import *
from .forms import LoginForm, CreateUserForm, EditUserForm, ResetPasswordForm
from .models import Users, UserStatus
from .users_service import get_user_by_id, check_user_permission

user_bp = Blueprint('user', __name__, template_folder='templates')


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = db.session.query(Users).filter_by(login=form.login.data.lower()).filter_by(
            status=UserStatus.ACTIVE).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            logger.info('Login {}'.format(user))
            redirect_url = request.args.get('next') or url_for('frontend.index')
            return redirect(redirect_url)
        else:
            flash("Invalid login or password", 'danger')
            return render_template('login.html', form=form)
    else:
        if not current_user.is_authenticated:
            ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            logger.debug("Unknown user try to connect to the application. IP: {}".format(ip_addr))
        return render_template('login.html', form=form)


@user_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('user.login'))


@login_manager.user_loader
def load_user(auth_id):
    return db.session.query(Users).filter_by(auth_id=auth_id).filter_by(status=UserStatus.ACTIVE).first()


@user_bp.route('/create_user', methods=['GET', 'POST'])
@login_required
@is_admin
def create_user():
    form = CreateUserForm(request.form)
    if form.validate_on_submit():
        user = Users()
        user.login = form.login.data.lower()
        user.role = form.role.data
        user.telegram_id = form.chat_id.data
        user.owner_id = current_user.id
        user.status = form.status.data
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)

        flash('User "{}" successfully created'.format(user.login), 'success')
        logger.info("'{}' created {}".format(current_user.login, user))

        return redirect(url_for('user.users_list'))
    else:
        return render_template('create_user.html', form=form)


@user_bp.route('/edit_user/', defaults={'user_id': 0})
@user_bp.route('/edit_user/<user_id>', methods=['GET', 'POST'])
@login_required
@is_admin
def edit_user(user_id):
    user = get_user_by_id(user_id)

    if not user:
        flash("User not found", 'info')
        return redirect(url_for('user.users_list'))

    if user.is_super_admin:
        flash("You can't change the system user", 'info')
        return redirect(url_for('user.users_list'))

    if not check_user_permission(user):
        flash("You don't have permission to edit this user", 'info')
        return redirect(url_for('user.users_list'))

    form = EditUserForm(request.form)

    if form.validate_on_submit():
        user.telegram_id = form.chat_id.data
        user.role = form.role.data
        user.status = form.status.data

        if form.password.data:
            user.set_password(form.password.data)

        db.session.commit()
        db.session.refresh(user)

        logger.info("'{}' updated {}".format(current_user.login, user))

        return redirect(url_for('user.users_list'))
    else:
        form.login.data = user.login
        form.role.data = user.role
        form.chat_id.data = user.telegram_id
        form.status.data = user.status
        form.user_id.data = user.id
        return render_template('create_user.html', form=form)


@user_bp.route('/users_list/', defaults={'page': 1})
@user_bp.route('/users_list/<int:page>')
@login_required
@is_admin
def users_list(page):
    query = db.session.query(Users)

    search = request.args.get('search')
    if search:
        search = '%' + search + '%'
        query = query.filter(or_(Users.login.ilike(search),
                                 Users.telegram_id.ilike(search),
                                 Users.status.ilike(search),
                                 Users.role.ilike(search)))

    total_count = query.count()

    if not current_user.is_super_admin:
        query = query.filter(or_(Users.owner_id == current_user.id, Users.id == current_user.id))

    query = query.order_by(Users.id).offset((page - 1) * current_app.config['PAGINATION_PAGE_SIZE']). \
        limit(current_app.config['PAGINATION_PAGE_SIZE'])

    users_list_result = query.all()

    pagination = Pagination(page=page,
                            per_page=current_app.config['PAGINATION_PAGE_SIZE'],
                            total_count=total_count,
                            filter_text=search)

    return render_template('users_list.html', users_list=users_list_result, roles=UserRole, pagination=pagination)


@user_bp.route('/delete_user/<user_id>')
@login_required
@is_admin
def delete_user(user_id):
    user = get_user_by_id(user_id)

    if not user:
        flash("User not found", 'info')
        return redirect(url_for('user.users_list'))

    if user.is_super_admin:
        flash("You can't change the system user", 'info')
        return redirect(url_for('user.users_list'))

    if not check_user_permission(user):
        flash("You don't have permission to edit this user", 'info')
        return redirect(url_for('user.users_list'))

    flash('User "{}" successfully deleted'.format(user.login), 'success')
    logger.info("'{}' deleted {}".format(current_user.login, user))

    db.session.query(Users).filter_by(id=user_id).delete()
    db.session.commit()

    return redirect(url_for('user.users_list'))


@user_bp.route('/send_message', methods=['POST'])
@login_required
@is_admin
def send_message():
    user_id = request.form.get('user_id')
    message_text = request.form.get('message_text')

    user = get_user_by_id(user_id)

    if not message_text.strip():
        flash("Enter a message", 'info')
        return redirect(url_for('user.users_list'))

    if not user:
        flash("User not found", 'info')
        return redirect(url_for('user.users_list'))

    if not user.telegram_id:
        flash("User doesn't have telegram_id", 'info')
        return redirect(url_for('user.users_list'))

    if not check_user_permission(user):
        flash("You don't have permission to send message this user", 'info')
        return redirect(url_for('user.users_list'))

    message_text = 'Message from "{}".\n\n{}'.format(current_user.login, message_text)
    add_notification(text=message_text, chat_id=user.telegram_id)

    flash('The message to "{}" was successfully sent'.format(user.login), 'success')

    return redirect(url_for('user.users_list'))


@user_bp.route('/reset_password_user/<user_id>')
@login_required
@is_admin
def reset_password_user(user_id):
    user = get_user_by_id(user_id)

    if not user:
        flash("User not found", 'info')
        return redirect(url_for('user.users_list'))

    if user.is_super_admin:
        flash("You can't change the system user", 'info')
        return redirect(url_for('user.users_list'))

    if not check_user_permission(user):
        flash("You don't have permission to edit this user", 'info')
        return redirect(url_for('user.users_list'))

    user.status = UserStatus.RESET
    user.set_reset_code()
    db.session.commit()

    reset_url = current_app.config['DOMAIN_NAME'] + url_for('user.change_password_user', user_id=user_id,
                                                            reset_code=user.reset_code)

    flash('User "{}" is now inactive. Activation link: {}'.format(user.login, reset_url), 'success')

    if user.telegram_id:
        message_text = '"{}"\n\nYour account status has changed to inactive. ' \
                       'To activate, set new password on this link:\n\n{}'.format(user.login, reset_url)
        add_notification(text=message_text, chat_id=user.telegram_id)

        flash("Message with a activation link was successfully sent", 'success')
    else:
        flash("Message with a activation link was not sent, because chat_id is empty", 'warning')

    logger.info("'{}' reset account {}".format(current_user.login, user))

    return redirect(url_for('user.users_list'))


@user_bp.route('/change_password_user/<user_id>/<reset_code>', methods=['GET', 'POST'])
def change_password_user(user_id, reset_code):
    user = get_user_by_id(user_id)

    if not user:
        flash("User not found", 'info')
        return redirect(url_for('user.login'))

    if reset_code and user.reset_code != reset_code:
        flash('Incorrect reset code', 'danger')
        return redirect(url_for('user.login'))

    if user.status != UserStatus.RESET:
        flash('Account is already activated', 'warning')
        return redirect(url_for('user.login'))

    form = ResetPasswordForm(request.form)

    if form.validate_on_submit():
        user.status = UserStatus.ACTIVE
        user.set_password(form.password.data)

        db.session.commit()
        db.session.refresh(user)

        logger.info("User '{}' set new password".format(user.login))

        flash('Please login with the new password', 'info')
        return redirect(url_for('user.login'))
    else:
        form.login.data = user.login
        return render_template('change_password.html', form=form)
