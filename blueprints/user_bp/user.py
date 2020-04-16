from flask import request, current_app, render_template, flash, redirect, url_for
from flask_login import login_required, current_user, fresh_login_required

from constant import HttpMethods, Permission
from decorators import confirm_user, permission_required
from utils import redirect_back, flash_errors
from extension import avatars, db
from models import User, Photo, Collect
from notifications import push_follow_notification
from forms.auth import (EditProfileForm, NotificationSettingForm, PrivacySettingForm,
                        UploadAvatarForm, DeleteAccountForm, CropAvatarForm,
                        ChangePasswordForm, ChangeEmailForm)
from . import user_bp


@user_bp.route("/<username>")
def index(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["PHOTO_PER_PAGE"]
    pagination = Photo.query.with_parent(user).order_by(Photo.timestamp.desc()).paginate(page, per_page)
    photos = pagination.items
    return render_template("user/index.html", user=user, pagination=pagination, photos=photos)


@user_bp.route("/settings/profile", methods=HttpMethods.methods_to_list())
@login_required
@confirm_user
@permission_required(Permission.anonymous_user())
def edit_profile():
    edit_profile_form = EditProfileForm()
    return render_template("user/settings/edit_profile.html", form=edit_profile_form)


@user_bp.route("/settings/password", methods=HttpMethods.methods_to_list())
@fresh_login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit() and current_user.check_password(form.old_password.data):
        current_user.set_password(form.password.data)
        db.session.commit()
        flash("Password updated", "success")
        return redirect(url_for(".index", username=current_user.username))
    return render_template("user/settings/change_password.html",form=form)


@user_bp.route("/settings/email", methods=HttpMethods.methods_to_list())
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        new_email = form.new_email.data
        old_email = form.old_email.data
        if User.query.filter_by(email=new_email).first():
            flash("User's email is already exists.", "warning")
            return redirect(url_for(".change_email_request"))
        user = User.query.filter_by(email=old_email).first()
        user.email = new_email
        db.session.commit()
        flash("Your email is updated.", "success")
    form.old_email.data = current_user.email
    return render_template("user/settings/change_email.html", form=form)


@user_bp.route("/settings/privacy")
@login_required
def privacy_setting():
    form = PrivacySettingForm()
    if form.validate_on_submit():
        current_user.public_collections = form.public_collections.data
        db.session.commit()
        flash("Privacy settings updated", "success")
        return redirect(url_for(".index", username=current_user.username))
    form.public_collections.data = current_user.public_collections
    render_template("user/settings/edit_privacy.html", form=form)


@user_bp.route("/settings/account")
@login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        db.session.delete(current_user._get_current_object())
        db.session.commit()
        flash("You are free,goodbye!", "success")
        return redirect(url_for("main.index"))
    return render_template("user/settings/delete_account.html", form=form)


@user_bp.route("/settings/avatar")
def change_avatar():
    upload_form = UploadAvatarForm()
    crop_form = CropAvatarForm()
    return render_template("user/settings/change_avatar.html",
                           upload_form=upload_form, crop_form=crop_form)


@user_bp.route("/settings/notification", methods=HttpMethods.methods_to_list())
@login_required
def notification_setting():
    form = NotificationSettingForm()
    if form.validate_on_submit():
        current_user.receive_collect_notification = form.receive_collect_notification.data
        current_user.receive_follow_notification = form.receive_follow_notification.data
        current_user.receive_comment_notification = form.receive_comment_notification.data
        db.session.commit()
        flash("Notification settings updated.", "success")
        return redirect(url_for(".index", username=current_user.username))
    form.receive_comment_notification.data = current_user.receive_comment_notification
    form.receive_follow_notification.data = current_user.receive_follow_notification
    form.receive_collect_notification.data = current_user.receive_collect_notification
    return render_template("user/settings/edit_notification.html", form=form)


@user_bp.route("/settings/avatar/upload", methods=[HttpMethods.post.value])
@login_required
@confirm_user
def upload_avatar():
    form = UploadAvatarForm()
    if form.validate_on_submit():
        image = form.image.data
        filename = avatars.save_avatar(image)
        current_user.avatar_raw = filename
        db.session.commit()
        flash("Image uploaded,please crop.", "success")
    flash_errors(form)
    return redirect(url_for(".change_avatar"))


@user_bp.route("/settings/avatar/crop", methods=[HttpMethods.post.value])
@login_required
@confirm_user
def crop_avatar():
    form = CropAvatarForm()
    if form.validate_on_submit():
        x = form.x.data
        y = form.y.data
        w = form.w.data
        h = form.h.data

        filenames = avatars.crop_avatar(current_user.avatar_raw, x, y, w, h)
        current_user.avatar_s = filenames[0]
        current_user.avatar_m = filenames[1]
        confirm_user.avatar_l = filenames[2]
        db.session.commit()
        flash("Avatar updated", "success")
    flash_errors(form)
    return redirect(url_for(".change_avatar"))


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
    if user.receive_follow_notification:
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
