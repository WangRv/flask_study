import os

from PIL import Image
from flask import current_app, request, redirect, flash, url_for
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from constant import Operations
from extension import db
from uuid import uuid4  # not parameters
# exceptions
from itsdangerous import BadSignature, SignatureExpired


def generate_token(user, operation, expire_in=None, **kwargs):
    """generate token for user"""
    s = Serializer(current_app.config["SECRET_KEY"], expire_in)
    data = {"id": user.id, "operation": operation.value}  # interval
    data.update(**kwargs)

    return s.dumps(data)


def validate_token(user, token, operation, new_password=None):
    """validate token for the request"""
    s = Serializer(current_app.config["SECRET_KEY"])
    try:
        data = s.loads(token)

    except (BadSignature, SignatureExpired):
        return False

    if operation.value != data.get("operation") or user.id != data["id"]:
        return False
    # confirm user to valid.
    if operation.value == Operations.CONFIRM.value:
        user.confirmed = True
    # reset user password
    elif operation.value == Operations.REST_PASSWORD.value:
        user.set_password(new_password)
    else:
        return False

    db.session.commit()
    return True


def redirect_back():
    """:return main.index or parameter the next"""
    next_url = request.args.get("next")
    if next_url:
        return redirect(next_url)
    else:
        return redirect(url_for("main.index"))


def random_file_name(name):
    """generate a new random file name"""
    ext = os.path.splitext(name)[1]  # get suffix of file name
    new_file_name = uuid4().hex + ext
    return new_file_name


def resize_image(image, filename, base_width):
    """resize image to  generate different  size image"""
    filename, ext = os.path.splitext(filename)
    img = Image.open(image)
    if img.size[0] <= base_width:
        return filename + ext  # not resize the image.
    w_percent = (base_width / float(img.size[0]))  # width percent
    h_size = int(img.size[1]) * w_percent
    img = img.resize((base_width, int(h_size)), Image.ANTIALIAS)

    filename += current_app.config["PHOTO_SUFFIX"][base_width] + ext
    img.save(os.path.join(current_app.config["UPLOAD_PATH"], filename), optimize=True, quality=True)
    return filename


def flash_errors(form):
    """extracting all errors from form into the flash"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in the {getattr(form, field).label.text} - {error}")
