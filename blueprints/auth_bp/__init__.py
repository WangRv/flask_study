from flask import Blueprint
from extension import login_manager
from models import User


@login_manager.user_loader
def user_login(id):
    user = User.query.get(id)
    return user


auth_bp = Blueprint("auth", __name__)
# set login view
login_manager.login_view = "auth.login"
from .auth import *
