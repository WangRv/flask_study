from . import auth_bp


@auth_bp.route("/login")
def login(): return "Login from blue print auth"


@auth_bp.route("/logout")
def logout(): pass
