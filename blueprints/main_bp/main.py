import os

from . import main_bp
from flask import render_template, request, flash, current_app, send_from_directory, redirect, url_for, abort
from constant import HttpMethods, Permission
from flask_login import login_required, current_user
from decorators import confirm_user, permission_required
from utils import random_file_name, flash_errors
from models import Photo, Tag, Collect
from extension import db
from forms.photo import DescriptionForm, TagForm


@main_bp.route("/")
def index():
    return render_template("main/index.html")


@main_bp.route("/explore")
def explore(): pass


@main_bp.route("/search")
def search(): pass


@main_bp.route("/show-notifications")
def show_notifications(): pass


@main_bp.route("/photo/<int:photo_id>")
def show_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    description = DescriptionForm()
    description.description.data = photo.description
    tag_form = TagForm()
    return render_template("main/photo.html", photo=photo, description_form=description, tag_form=tag_form)


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
