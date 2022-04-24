from functools import wraps

from flask_login import current_user
from flask import redirect, url_for

from .models import UserRole


def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            return redirect(url_for('frontend.index'))
        return f(*args, **kwargs)

    return wrap


def is_super_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in [UserRole.SUPER_ADMIN]:
            return redirect(url_for('frontend.index'))
        return f(*args, **kwargs)

    return wrap
