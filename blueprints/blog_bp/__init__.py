from flask import (
    Blueprint,
    render_template,
    url_for, request,
    current_app, abort, make_response,
    flash, redirect)
from flask_login import current_user, login_required
# import database model
from ... import db, Post, Category, Comment
# import view forms
from ... import AdminCommentForm, CommentForm
# import utility
from ... import send_new_comment_email, send_new_reply_email

blog_bp = Blueprint("blog", __name__)


# login protect
@blog_bp.before_request
@login_required
def login_protect(): pass


from .views import *
