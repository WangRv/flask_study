import os

from . import main_bp
from flask import render_template, request, flash, current_app, send_from_directory, redirect, url_for, abort
from constant import HttpMethods, Permission
from flask_login import login_required, current_user
from decorators import confirm_user, permission_required
from utils import random_file_name, resize_image
from models import Photo
from extension import db


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
    return render_template("main/photo.html", photo=photo)


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
    return redirect(url_for(".show_photo", photo_id=photo_n.id))


@main_bp.route("/delete-photo/<int:photo_id>", methods=[HttpMethods.post.value])
@login_required
def delete_photo(photo_id):
    # @todo unfinished
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
