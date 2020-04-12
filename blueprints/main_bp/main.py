import os

from . import main_bp
from flask import render_template, request, flash, current_app, send_from_directory, redirect, url_for, abort
from constant import HttpMethods, Permission, QueryRule
from flask_login import login_required, current_user
from decorators import confirm_user, permission_required
from utils import random_file_name, flash_errors
from models import Photo, Tag, Collect, Comments, Notification
from extension import db
from forms.photo import DescriptionForm, TagForm, CommentForm
from notifications import push_collect_notification, push_comment_notification


@main_bp.route("/")
def index():
    return render_template("main/index.html")


@main_bp.route("/explore")
def explore(): pass


@main_bp.route("/search")
def search(): pass


@main_bp.route("/show-notifications")
@login_required
def show_notifications():
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("NOTIFICATION_PER_PAGE", 10)
    notifications = Notification.query.with_parent(current_user)
    filter_rule = request.args.get("filter")
    if filter_rule == QueryRule.unread.value:
        notifications = notifications.filter_by(is_read=False)
    pagination = notifications.order_by(Notification.timestamp.desc()).paginate(page, per_page)
    notifications = pagination.items
    return render_template("main/notifications.html", pagination=pagination, notifications=notifications)


@main_bp.route("/notification/read/<int:notification_id>", methods=[HttpMethods.post.value])
@login_required
def read_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if current_user != notification.receiver:
        abort(403)
    notification.is_read = True
    db.session.commit()
    flash("Notification archived", "success")
    return redirect(url_for(".show_notifications"))


@main_bp.route("/notification/read/all", methods=[HttpMethods.post.value])
@login_required
def read_all_notification():
    for notification in current_user.notifications:
        # all set true for the each user's notification
        notification.is_read = True
    db.session.commit()
    flash("All notifications archived", "success")
    return redirect(url_for(".show_notifications"))


@main_bp.route("/photo/<int:photo_id>")
def show_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    description = DescriptionForm()
    description.description.data = photo.description
    tag_form = TagForm()
    comment_form = CommentForm()
    page = request.args.get("page", type=int)
    per_page = current_app.config.get("COMMENT_PER_PAGE", 10)
    pagination = Comments.query.with_parent(photo).order_by(
        Comments.timestamp.desc()).paginate(page, per_page)
    comments = pagination.items
    return render_template("main/photo.html", photo=photo,
                           description_form=description, tag_form=tag_form,
                           comment_form=comment_form, pagination=pagination,
                           comments=comments)


@main_bp.route("/photo/<int:photo_id>/description", methods=[HttpMethods.post.value])
@login_required
@permission_required(Permission.normal_user())
def edit_description(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if current_user != photo.author:
        abort(404)
    form = DescriptionForm()
    if form.validate_on_submit():
        photo.description = form.description.data
        db.session.commit()
        flash("Description updated", "success")
    flash_errors(form)
    return redirect(url_for(".show_photo", photo_id=photo_id))


@main_bp.route("/photo/<int:photo_id>/tag/new", methods=[HttpMethods.post.value])
@login_required
def new_tag(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if current_user != photo.author:
        abort(404)
    form = TagForm()
    if form.validate_on_submit():
        for name in form.tag.data.split():
            tag = Tag.query.filter_by(name=name).first()
            if tag is None:
                tag = Tag(name=name)
                db.session.add(tag)
                db.session.commit()
            if tag not in photo.tags:
                photo.tags.append(tag)
                db.session.commit()
        flash("Tag added", "success")
    flash_errors(form)
    return redirect(url_for(".show_photo", photo_id=photo_id))


@main_bp.route("/delete/tag/<int:photo_id>/<int:tag_id>", methods=[HttpMethods.post.value])
@login_required
def delete_tag(photo_id, tag_id):
    tag = Tag.query.get_or_404(tag_id)
    photo = Photo.query.get_or_404(photo_id)
    if current_user != photo.author:
        abort(403)
    photo.tags.remove(tag)
    db.session.commit()

    if not tag.photos:
        db.session.delete(tag)
        db.session.commit()
    flash("Tag deleted.", "info")
    return redirect(url_for(".show_photo", photo_id=photo_id))


@main_bp.route("/tag/<int:tag_id>", defaults={"order": "by_time"})
@main_bp.route("/tag/<int:tag_id>/<order>")
def show_tag(tag_id, order):
    tag = Tag.query.get_or_404(tag_id)
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["PHOTO_PER_PAGE"]
    order_rule = "time"
    pagination = Photo.query.with_parent(tag).order_by(Photo.timestampde.desc()).paginate(page, per_page)
    photos = pagination.items
    if order == "by_collects":
        photos.sort(key=lambda x: len(x.collectors), reverse=True)
        order_rule = "collects"
    return render_template("main/tag.html", tag=tag, pagination=pagination, photos=photos, order_rule=order_rule)


@main_bp.route("/collect/<int:photo_id>", methods=[HttpMethods.post.value])
@login_required
@confirm_user
@permission_required(Permission.COLLECT.value)
def collect(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if current_user.is_collecting_photo(photo):
        flash("Already collected.", "info")
        return redirect(url_for(".show_photo", photo_id=photo_id))
    current_user.collect(photo)
    push_collect_notification(current_user, photo_id, photo.author)
    flash("Photo collected", "success")
    return redirect(url_for(".show_photo", photo_id=photo_id))


@main_bp.route("/uncollected/<int:photo_id>", methods=[HttpMethods.post.value])
@login_required
def uncollected(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if not current_user.is_collecting_photo(photo):
        flash("You not collected this photo.", "info")
    current_user.uncollected(photo)
    flash("Photo uncollected", "info")
    return redirect(url_for(".show_photo", photo_id=photo_id))


@main_bp.route("/photo/<int:photo_id>/collectors")
def show_collectors(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("USER_PER_PAGE", 5)
    pagination = Collect.query.with_parent(photo).order_by(Collect.timestamp.asc()).paginate(page, per_page)
    collects = pagination.items
    return render_template("main/collectors.html", collects=collects, photo=photo, pagination=pagination)


@main_bp.route("/photo/<int:photo_id>/set-comment",
               methods=[HttpMethods.post.value])
@login_required
def set_comment(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if current_user != photo.author:
        abort(404)
    condition = photo.can_comment
    if condition:
        photo.can_comment = False
        flash("Photo comments disable", "info")
    else:
        photo.can_comment = True
        flash("Photo comments enable", "info")
    db.session.commit()
    return redirect(url_for(".show_photo", photo_id=photo_id))


@main_bp.route("/photo/<int:photo_id>/new-comment",
               methods=[HttpMethods.post.value])
@login_required
@permission_required(Permission.COMMENT.value)
def new_comment(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        comment = Comments(body=comment_form.body.data,
                           author=current_user._get_current_object(),
                           photo=photo)

        if request.args.get("reply"):
            replied = Comments.query.get_or_404(request.args.get("reply", type=int))
            comment.replied = replied

        db.session.add(comment)
        db.session.commit()
    page = request.args.get("page", 1)
    # User notification

    push_comment_notification(photo_id, photo.author, page)
    return redirect(url_for(".show_photo", photo_id=photo_id, page=page))


@main_bp.route("/photo/<int:comment_id>/reply-comment")
@login_required
@permission_required(Permission.COMMENT.value)
def reply_comment(comment_id):
    comment = Comments.query.get_or_404(comment_id)
    if comment.author == comment.author:
        abort(404)
    photo_id = comment.photo_id
    reply = comment.id
    return redirect(url_for(".show_photo", photo_id=photo_id, reply=reply))


@main_bp.route("/photo/<int:comment_id>/delete-comment",
               methods=[HttpMethods.post.value])
@login_required
def delete_comment(comment_id):
    comment = Comments.query.get_or_404(comment_id)
    if not current_user.can_permission(Permission.MODERATE.value) or \
            current_user != comment.author:
        abort(404)
    photo_id = comment.photo_id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for(".show_photo", photo_id=photo_id))


@main_bp.route("/photo/<int:comment_id>/report-comment")
@login_required
@permission_required(Permission.normal_user())
def report_comment(comment_id):
    comment = Comments.query.get_or_404(comment_id)
    if current_user == comment.author:
        abort(404)
    comment.flag += 1
    db.session.commit()
    return redirect(url_for(".show_photo", photo_id=comment.photo_id))


@main_bp.route("/photo/n/<int:photo_id>")
def photo_next(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    photo_n = Photo.query.with_parent(photo.author).filter(Photo.id < photo.id).order_by().first()
    if photo_n is None:
        flash("This is already the last one.", "info")
        return redirect(url_for(".show_photo", photo_id=photo_id))
    return redirect(url_for(".show_photo", photo_id=photo_n.id))


@main_bp.route("/photo/p/<int:photo_id>")
def photo_previous(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    photo_n = Photo.query.with_parent(photo.author).filter(Photo.id > photo.id).order_by(Photo.id.asc()).first()
    if photo_n is None:
        flash("This is already the first one.", "info")
        return redirect(url_for(".show_photo", photo_id=photo.id))
    return redirect(url_for(".show_photo", photo_id=photo_n.id))


@main_bp.route("/delete-photo/<int:photo_id>", methods=[HttpMethods.post.value])
@login_required
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if current_user != photo.author:
        abort(403)
    db.session.delete(photo)
    db.session.commit()
    flash("Photo deleted", "info")

    photo_n = Photo.query.with_parent(photo.author).filter(Photo.id < photo_id).order_by(Photo.id.desc()).first()
    if photo_n is None:
        photo_p = Photo.query.with_parent(photo.author).filter(Photo.id > photo_id).order_by(Photo.id.asc()).first()
        if photo_p is None:  # empty
            return redirect(url_for("user.index", username=photo.author.username))
        return redirect(url_for(".show_photo", photo_id=photo_p.id))
    return redirect(url_for(".show_photo", photo_id=photo_n.id))


@main_bp.route("/report/photo/<int:photo_id>", methods=[HttpMethods.post.value])
@login_required
@confirm_user
def report_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    photo.flag += 1
    db.session.commit()
    flash("Photo reported", "success")
    return redirect(url_for(".show_photo", photo_id=photo_id))


@main_bp.route("/upload", methods=HttpMethods.methods_to_list())
@login_required
@confirm_user
@permission_required(Permission.UPLOAD.value)
def upload():
    if request.method == HttpMethods.post.value and "file" in request.files:
        f = request.files.get("file")
        filename = random_file_name(f.filename)
        # first to save a image then to save to database.
        f.save(os.path.join(current_app.config["UPLOAD_PATH"], filename))
        photo = Photo(filename=filename, author=current_user._get_current_object())
        photo.generate_different_size_photo()

        db.session.add(photo)
        db.session.commit()
    return render_template("main/upload.html")


@main_bp.route("/avatars/<path:filename>")
def get_avatar(filename):
    return send_from_directory(current_app.config["AVATARS_SAVE_PATH"], filename)


@main_bp.route("/uploads/<path:filename>")
def get_image(filename):
    return send_from_directory(current_app.config["UPLOAD_PATH"], filename)
