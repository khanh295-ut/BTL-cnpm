from functools import wraps
from flask import abort
from flask_login import current_user, login_required


def admin_required(func):
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "Admin":
            abort(403)
        return func(*args, **kwargs)

    return wrapper


def self_or_admin(func):
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        user_id = kwargs.get("user_id")
        if current_user.role == "Admin" or current_user.id == int(user_id):
            return func(*args, **kwargs)
        abort(403)

    return wrapper
