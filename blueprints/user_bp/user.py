from flask import request, current_app, render_template
from . import user_bp
from models import User, Photo, Collect


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
