from flask import request, current_app, render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from constant import HttpMethods, Permission
from decorators import confirm_user, permission_required
from utils import redirect_back
from models import User, Photo, Collect
from notifications import push_follow_notification
from . import user_bp


@user_bp.route("/<username>")
def index(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["PHOTO_PER_PAGE"]
    pagination = Photo.query.with_parent(user).order_by(Photo.timestamp.desc()).paginate(page, per_page)
    photos = pagination.items
    return render_template("user/index.html", user=user, pagination=pagination, photos=photos)


@user_bp.route("/edit-profile")
def edit_profile(): pass


@user_bp.route("/show-collections/<username>")
def show_collections(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("PHOTO_PER_PAGE", 5)
    pagination = Collect.query.with_parent(user).order_by(Collect.timestamp.desc()).paginate(page, per_page)
    collects = pagination.items

    return render_template("user/collections.html", pagination=pagination, user=user, collects=collects)


@user_bp.route("<username>/followers/")
def show_followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("USER_PER_PAGE", 10)
    pagination = user.followers.paginate(page, per_page)
    follows = pagination.items
    return render_template("user/followers.html", user=user, follows=follows)


@user_bp.route("<username>/following")
def show_following(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("USER_PER_PAGE", 10)
    pagination = user.following.paginate(page, per_page)
    follows = pagination.items
    return render_template("user/following.html", user=user, follows=follows)


@user_bp.route("/change-avatar")
def change_avatar(): pass


@user_bp.route("/follow/<username>", methods=[HttpMethods.post.value])
@login_required
@confirm_user
@permission_required(Permission.FOLLOW.value)
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user):
        flash("Already followed", "info")
        return redirect(url_for(".index", username=username))
    current_user.follow(user)
    flash("User followed.", "info")
    push_follow_notification(follower=current_user, receiver=user)
    return redirect_back()


@user_bp.route("/unfollow/<username>", methods=[HttpMethods.post.value])
@login_required
def unfollow(username):
    user = User.query.fillter_by(username=username).first_or_404()
    if not current_user.is_following(user):
        flash("Not follow yet", "info")
        return redirect(url_for(".index", username=username))
    current_user.unfollow(user)
    flash("User unfollowed", "info")
    return redirect_back()
