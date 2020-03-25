from flask import redirect, flash, render_template, url_for
from . import auth_bp
from ...utils import redirect_back
from ...forms import LoginForm
from ...db_model import Admin
from flask_login import current_user, login_required, login_user, logout_user


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("blog.index"))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.first()
        if admin:
            if username == admin.username and admin.check_password(password):
                login_user(admin, remember)
                flash("Success login.", "success")
                return redirect_back()
            else:
                flash("Not account", "warning")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    flash("Logout success", "info")
    logout_user()
    return redirect_back()
