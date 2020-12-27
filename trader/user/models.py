from flask_login import UserMixin
from string import ascii_letters, digits
from random import choice
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db


class UserRole:
    GROUP = 'GROUP'
    USER = 'USER'
    ADMIN = 'ADMIN'
    SUPER_ADMIN = 'SUPER_ADMIN'

    @staticmethod
    def get_new_user_roles_list():
        return ['GROUP', 'USER', 'ADMIN']


class UserStatus:
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    RESET = 'RESET'

    @staticmethod
    def get_new_user_statuses_list():
        return ['ACTIVE', 'INACTIVE']


class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    telegram_id = db.Column(db.Integer)
    owner_id = db.Column(db.Integer)
    status = db.Column(db.String, nullable=False)
    reset_code = db.Column(db.String)
    auth_id = db.Column(db.String, nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)
        self.auth_id = self.login + '_' + str(uuid.uuid4())

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_reset_code(self):
        self.reset_code = ''.join([choice(ascii_letters + digits) for _ in range(64)])

    def get_id(self):
        return self.auth_id

    @property
    def is_active(self):
        if self.status == UserStatus.ACTIVE:
            return True
        return False

    @property
    def is_admin(self):
        if self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            return True
        return False

    @property
    def is_super_admin(self):
        if self.role == UserRole.SUPER_ADMIN:
            return True
        return False

    def __repr__(self):
        return "<User(id='%s', login='%s', role='%s', telegram_id='%s', owner_id='%s', status='%s')>" % (
            self.id, self.login, self.role, self.telegram_id, self.owner_id, self.status)
