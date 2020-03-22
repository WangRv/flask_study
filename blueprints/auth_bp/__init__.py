from flask import Blueprint,redirect,url_for,render_template,flash
from flask_login import current_user,login_user,logout_user,login_required
from ... import LoginForm,Admin,redirect_back

auth_bp = Blueprint("auth", __name__)
from .auth import *
