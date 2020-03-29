from functools import wraps
from flask import Markup, flash, url_for, redirect
from flask_login import current_user


def confirm_user(func):
    """take charge to protect user view that only confirm user """

    @wraps(func)
    def decorate_function(*args, **kwargs):
        if not current_user.confirmed:
            message = Markup("Please confirm your account first.Not receive the email?"
                             f"<a class=\"alert-link\" href=\"{url_for('auth.resend_confirm_email')}\">")
            flash(message, "warning")
            return redirect(url_for("main.index"))
        return func(*args, **kwargs)

    return decorate_function
