from flask import url_for
from models import Notification
from extension import db


def push_follow_notification(follower, receiver):
    """use is followed notification"""
    message = f"User <a href=\"{url_for('user.index', username=follower.username)}\">" \
              f"{follower.username} followed you </a>"
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()


def push_comment_notification(photo_id, receiver, page=1):
    """Photo is commented notification"""
    message = f"<a href=\"{url_for('main.show_photo', photo_id=photo_id, page=page)}\">" \
              f"This photo </a> has new comment/reply."
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()


def push_collect_notification(collector, photo_id, receiver):
    """User's photo is collected notification"""
    message = f"User <a href=\"{url_for('user.index', username=collector.username)}\">{collector.username}</a>" \
              f"collected your <a href=\"{url_for('main.photo', photo_id=photo_id)}\">photo</a>"
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()
