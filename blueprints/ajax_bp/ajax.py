from . import ajax_bp
from flask import render_template, url_for
from models import User


@ajax_bp.route("/show-notifications")
def show_notifications(): pass


@ajax_bp.route("/notifications-count")
def notifications_count(): pass


@ajax_bp.route("/profile/<int:user_id>")
def get_profile(user_id):
    """simple user details"""
    user = User.query.get_or_404(user_id)
    return render_template("main/profile_popup.html", user=user)

