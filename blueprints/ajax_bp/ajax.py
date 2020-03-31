from . import ajax_bp


@ajax_bp.route("/show-notifications")
def show_notifications(): pass


@ajax_bp.route("/notifications-count")
def notifications_count(): pass
