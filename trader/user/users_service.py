from flask_login import current_user
from ..extensions import db
from .models import Users, UserStatus
from sqlalchemy import or_


def is_authorized_telegram_id(telegram_id):
    return db.session.query(Users).filter(Users.telegram_id == telegram_id).\
        filter(Users.status == UserStatus.ACTIVE).count()


def get_controlled_users():
    return db.session.query(Users.id, Users.login, Users.telegram_id).\
        filter(or_(Users.id == current_user.id, Users.owner_id == current_user.id)).\
        filter(Users.status == UserStatus.ACTIVE).all()


def get_user_by_id(user_id):
    return db.session.query(Users).filter(Users.id == user_id).first()


def get_user_by_telegram_id(telegram_id):
    return db.session.query(Users).filter(Users.telegram_id == telegram_id).first()


def check_user_permission(user):
    return current_user.is_super_admin or current_user.id == user.id or current_user.id == user.owner_id
