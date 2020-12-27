from ..extensions import db
from .models import Users, UserStatus


def get_telegram_users():
    users = db.session.query(Users.telegram_id).filter(Users.telegram_id is not None).filter(
       Users.status == UserStatus.ACTIVE).all()
    users = [r[0] for r in users]
    return users
