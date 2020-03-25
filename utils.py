from .extension_module import login_manager
from flask import request, url_for, redirect
from .db_model import Admin

# set to redirect
login_manager.login_view = "auth.login"
login_manager.login_message = "You must be login."
login_manager.login_message_category = "warning"

# login function
@login_manager.user_loader
def login_user(user_id):
    user = Admin.query.get(user_id)
    return user

# redirect back
def redirect_back():
    next_url = request.args.get("next")
    if next_url:
        return redirect(next_url)
    else:
        return redirect(url_for("blog.index"))
