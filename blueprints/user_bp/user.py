from . import user_bp


@user_bp.route("/")
def index(): pass


@user_bp.route("/edit-profile")
def edit_profile(): pass


@user_bp.route("/show-collections/<username>")
def show_collections(username): pass
