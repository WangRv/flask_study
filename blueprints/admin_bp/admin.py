from . import admin_bp
from flask import flash, render_template, request, current_app, redirect, url_for
from models import User, Role, Photo, Tag, Comments
from decorators import admin_required
from forms.admin import EditProfileAdminForm
from extension import db
from utils import redirect_back
from constant import HttpMethods


@admin_bp.route("/index")
def index():
    photo_count = Photo.query.count()
    user_count = User.query.count()
    locked_user_count = User.query.filter_by(locked=True).count()
    blocked_user_count = User.query.filter_by(active=False).count()
    comment_count = Comments.query.count()
    tag_count = Tag.query.count()
    return render_template("admin/index.html", photo_count=photo_count,
                           user_count=user_count, locked_user_count=locked_user_count,
                           blocked_user_count=blocked_user_count, comment_count=comment_count,
                           tag_count=tag_count)


@admin_bp.route("/profile/<int:user_id>")
@admin_required
def edit_profile_admin(user_id):
    user = User.query.get_or_404(user_id)
    form = EditProfileAdminForm(user)
    if form.validate_on_submit():
        user.name = form.name.data
        role = Role.query.get(form.role.data)
        if role.name == "Locked":
            user.lock()
        user.role = role
        user.bio = form.bio.data
        user.website = form.website.data
        user.active = form.active.data
        user.location = form.location.data
        user.email = form.email.data
        db.session.commit()
        flash("Profile updated", "success")
        return redirect_back()
    form.name.data = user.name
    form.role.data = user.role_id
    form.bio.data = user.bio
    form.website.data = user.website
    form.location.data = user.location
    form.user_name.data = user.username
    form.email.data = user.email
    form.confirmed.data = user.confirmed
    form.active.data = user.active
    return render_template("admin/edit_profile.html", form=form, user=user)


@admin_bp.route("/manage-photo", defaults={"order": "by_flag"})
@admin_bp.route("/manage-photo/<order>")
@admin_required
def manage_photo(order):
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("MANAGER_PHOTO_PER_PAGE", 10)
    order_rule = "flag"
    if order == "by_time":
        pagination = Photo.query.order_by(Photo.timestamp.desc()).paginate(page, per_page)
        order_rule = "time"
    else:
        pagination = Photo.query.order_by(Photo.flag.desc()).paginate(page, per_page)
    photos = pagination.items
    return render_template("admin/manage_photo.html", pagination=pagination, photos=photos,
                           order_rule=order_rule)


@admin_bp.route("/manage-user")
@admin_required
def manage_user():
    page = request.args.get("page", 1, type=int)
    per = current_app.config.get("USER_PER_PAGE", 10)
    pagination = User.query.order_by(User.member_since).paginate(page, per)
    users = pagination.items
    return render_template("admin/manage_user.html", users=users, pagination=pagination)


@admin_bp.route("/manage-tag")
@admin_required
def manage_tag():
    page = request.args.get("page", 1, type=int)
    per = current_app.config.get("TAG_PER_PAGE", 10)

    pagination = Tag.query.order_by(Tag.name).paginate(page, per)
    tags = pagination.items

    return render_template("admin/manage_tag.html", tags=tags, pagination=pagination)


@admin_bp.route("/manage-comment", defaults={"order": "by_flag"})
@admin_bp.route("/manage-comment/<order>")
@admin_required
def manage_comment(order):
    page = request.args.get("page", 1, type=int)
    per = current_app.config.get("PHOTO_PER_PAGE", 10)
    order_rule = "flag"
    if order == "by_time":

        pagination = Comments.query.order_by(Comments.timestamp.desc()).paginate(page, per)
        order_rule = "by_time"
    elif order == "by_flag":
        pagination = Comments.query.order_by(Comments.flag).paginate(page, per)
    comments = pagination.items
    return render_template("admin/manage_comment.html",
                           order_rule=order_rule, comments=comments, pagination=pagination)


@admin_bp.route("/block-user/<int:user_id>", methods=[HttpMethods.post.value])
@admin_required
def block_user(user_id):
    user = User.query.get_or_404(user_id)
    if not user.locked:
        user.lock()
        flash(f"{user.name}is locked.", "success")
        return redirect_back()
    flash(f"{user.name}is already locked.", "warning")
    return redirect_back()


@admin_bp.route("/delete-tag/<int:tag_id>", methods=[HttpMethods.post.value])
@admin_required
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return redirect(url_for(".index"))
