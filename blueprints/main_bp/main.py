import os

from . import main_bp
from flask import render_template, request, current_app
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
        filename_s = resize_image(f, filename, 400)
        filename_m = resize_image(f, filename, 800)
        photo = Photo(filename=filename, author=current_user._get_current_object())
        photo.filename_s = filename_s
        photo.filename_m = filename_m

        db.session.add(photo)
        db.session.commit()
    return render_template("main/upload.html")


@main_bp.route("/get-avatar")
def get_avatar(): pass
