from flask import current_app, request, redirect
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from constant import Operations
from extension import db
# exceptions
from itsdangerous import BadSignature, SignatureExpired


def generate_token(user, operation, expire_in=None, **kwargs):
    """generate token for user"""
    s = Serializer(current_app.config["SECRET_KEY"], expire_in)
    data = {"id": user.id, "operation": operation}  # interval
    data.update(**kwargs)

    return s.dumps(data)


def validate_token(user, token, operation, new_password=None):
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


# url function
def redirect_back():
    next_url = request.args.get("next")
    if next_url:
        return redirect(next_url)
    else:
        return redirect("main.index")
