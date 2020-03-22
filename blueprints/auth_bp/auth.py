from . import auth_bp, current_user, redirect, url_for, render_template, flash, LoginForm
from . import Admin, login_user, logout_user, redirect_back, login_required


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("blog.index"))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.first()
        if admin:
            if username == admin.username and admin.check_password(password):
                login_user(admin, remember)
                flash("Success login.")
                return redirect_back()
            else:
                flash("Not account", "warning")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    flash("Logout success", "info")
    logout_user()
    return redirect_back()
