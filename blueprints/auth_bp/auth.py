from . import auth_bp
from flask_login import current_user, login_required, login_user, logout_user
from flask import redirect, url_for, flash, render_template
from forms.auth import UserRegisterForm, LoginForm, ForgetForm, ResetPasswordForm
from models import User
# internal methods
from constant import HttpMethods
from extension import db
from utils import generate_token, validate_token, redirect_back
from constant import Operations
from emails import send_token_confirm_email, send_reset_password_email


@auth_bp.route("/register", methods=HttpMethods.methods_to_list())
def register():
    # if user is already logging.
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    # user logging form.
    form = UserRegisterForm()
    if form.validate_on_submit():
        name = form.username.data
        email = form.email.data.lower()
        username = form.username.data
        password = form.password.data
        # init user object to registry web
        user = User(name=name, email=email, username=username)
        user.set_password(password)
        user.set_role()  # default role is User.
        db.session.add(user)
        db.session.commit()
        token = generate_token(user=user, operation=Operations.CONFIRM.value)
        send_token_confirm_email(user, token)

        flash(f"Confirm email sent,check your email {form.email.data}", "info")
        return redirect(url_for(".login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=HttpMethods.methods_to_list())
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        remember = login_form.remember.data
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember)

            return redirect_back()
        else:
            flash("Invalid email or password", "warning")

    return render_template("auth/login.html", form=login_form)


@auth_bp.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if validate_token(current_user, token, Operations.CONFIRM.value):
        flash("Account confirmed", "success")
        return redirect(url_for("main.index"))
    else:
        # Invalid or expired token
        flash("Invalid or expired token.", "danger")
        return redirect(url_for(".reconfirm"))


@auth_bp.route("/resend-confirm-email", methods=[HttpMethods.post.value])
@login_required
def resend_confirm_email():
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    # User can send to confirm email again.
    else:
        token = generate_token(user=current_user, operation=Operations.CONFIRM)
        send_token_confirm_email(current_user, token)
        flash(f"Confirm email sent,check your email {current_user.email}", "info")
        return redirect(url_for(".login"))


@auth_bp.route("/logout", methods=HttpMethods.methods_to_list())
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect_back()


@auth_bp.route("/forget-password", methods=HttpMethods.methods_to_list())
def forget_password():
    if current_user.is_authenticated:
        return redirect_back()
    forget_form = ForgetForm()
    if forget_form.validate_on_submit():
        email = forget_form.email.data
        user = User.query.filter_by(email=email.lower()).first()
        if user:
            token = generate_token(user=user, operation=Operations.REST_PASSWORD.value)
            send_reset_password_email(user, token, email)
            flash("Password rest email sent,check your email. ", "warning")
            return redirect(url_for(".login"))
        flash("Invalid email.", "warning")
        return redirect(url_for(".forget_password"))
    return render_template("auth/reset_password.html", form=forget_form)


@auth_bp.route("/reset-password/<token>", methods=HttpMethods.methods_to_list())
def reset_password(token):
    if current_user.is_authenticated:
        redirect(url_for("main.index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None:
            return redirect_back()
        new_password = form.password.data
        if validate_token(user, token, operation=Operations.REST_PASSWORD, new_password=new_password):
            flash("Password updated", "success")
            return redirect(url_for(".login"))
        else:
            flash("Invalid or expired token.", "danger")
            return redirect(url_for(".forget_password"))
    return render_template("auth/reset_password.html", form=form)
