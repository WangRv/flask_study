from flask import request, current_app, render_template
from . import user_bp
from models import User, Photo


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
def show_collections(username): pass


@user_bp.route("/change-avatar")
def change_avatar(): pass
