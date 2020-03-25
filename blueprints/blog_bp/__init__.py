from flask import Blueprint

from flask_login import login_required

blog_bp = Blueprint("blog", __name__)


# login protect
@blog_bp.before_request
@login_required
def login_protect():
    pass


from .views import *
