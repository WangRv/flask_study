import blueprints.user_bp.user
from . import ajax_bp
from flask_login import current_user
from flask import render_template, url_for, jsonify
from models import User, Permission, Notification, Photo
from constant import HttpMethods


@ajax_bp.route("/show-notifications")
def show_notifications(): pass


@ajax_bp.route("/notifications-count")
def notifications_count():
    if not current_user.is_authenticated:
        return jsonify(message="Login required"), 403
    count = Notification.query.with_parent(current_user).filter_by(is_read=False).count()
    return jsonify(count=count)


@ajax_bp.route("/profile/<int:user_id>")
def get_profile(user_id):
    """simple user details"""
    user = User.query.get_or_404(user_id)
    return render_template("main/profile_popup.html", user=user)


@ajax_bp.route("/follow/<username>", methods=[HttpMethods.post.value])
def follow(username):
    if not current_user.is_authenticated:
        return jsonify(message="Login required."), 403
    if not current_user.comfirmed:
        return jsonify(message="Confirm account required."), 400
    if not current_user.can_permission(Permission.FOOLOW.value):
        return jsonify(message="No permission."), 403
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user):
        return jsonify(message="Already followed."), 400
    blueprints.user_bp.user.follow(user)
    return jsonify(message="User followed.")


@ajax_bp.route("/unfollow/<username>", methods=[HttpMethods.post.value])
def unfollow(username):
    if not current_user.is_authenticated:
        return jsonify(message="Login required"), 403
    user = User.query.filter_by(username=username).first_or_404()
    if not current_user.is_following(user):
        return jsonify(message="Not follow yet."), 400

    blueprints.user_bp.user.unfollow(user)
    return jsonify(message="Follow canceled.")


@ajax_bp.route("/followers-count/<int:user_id>")
def followers_count(user_id):
    user = User.query.get_or_404(user_id)
    count = user.followers.count() - 1
    return jsonify(count=count)


@ajax_bp.route("/collectors-count/<int:photo_id>", methods=[HttpMethods.get.value])
def collectors_count(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    count = len(photo.collectors)
    return jsonify(count=count)


@ajax_bp.route("/uncollect/<int:photo_id>", methods=[HttpMethods.post.value])
def uncollect(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if current_user.is_collecting_photo(photo):
        current_user.uncollected(photo)
        return jsonify(message="Photo uncollected.")


@ajax_bp.route("/collect/<int:photo_id>", methods=[HttpMethods.post.value])
def collect(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if not current_user.is_collecting_photo(photo):
        current_user.collect(photo)
    return jsonify(message="Photo collected.")
