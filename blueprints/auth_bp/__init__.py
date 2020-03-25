from flask import Blueprint
from ...extension_module import login_manager

auth_bp = Blueprint("auth", __name__)


# login function
@login_manager.user_loader
def login(user_id):
    user = Admin.query.get(user_id)
    return user


from .auth import *
