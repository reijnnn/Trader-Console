from ..extensions import db
from .models      import Users, User_status

def get_telegram_users():
   users = db.session.query(Users.telegram_id).filter(Users.telegram_id != None).filter(Users.status == User_status.ACTIVE).all()
   users = [r[0] for r in users]
   return users
