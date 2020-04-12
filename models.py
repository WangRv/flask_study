import os
from datetime import datetime
from flask import current_app
from flask_avatars import Identicon
from werkzeug.security import generate_password_hash, check_password_hash  # password security
from flask_login import UserMixin
from extension import db
from utils import resize_image


class Follow(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # relationship attributes
    follower = db.relationship("User", foreign_keys=[follower_id], back_populates="following", lazy="joined",
                               cascade="all")
    followed = db.relationship("User", foreign_keys=[followed_id], back_populates="followers", lazy="joined",
                               cascade="all")


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # User data
    username = db.Column(db.String(20), unique=True, index=True)
    email = db.Column(db.String(255), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(30))
    website = db.Column(db.String(255))
    bio = db.Column(db.String(120))
    location = db.Column(db.String(50))
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    # user status
    confirmed = db.Column(db.Boolean, default=False)
    # role relation with user, user only use one role. many to one...
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    role = db.relationship("Role", back_populates="users", uselist=False)
    # uploaded photos
    photos = db.relationship("Photo", back_populates="author", cascade="all")
    # user portrait
    avatar_s = db.Column(db.String(64))
    avatar_m = db.Column(db.String(64))
    avatar_l = db.Column(db.String(64))
    # collected photos
    collections = db.relationship("Collect", back_populates="collector", cascade="all")
    # user comments
    comments = db.relationship("Comments", back_populates="author", cascade="all")
    # follow attributes
    following = db.relationship("Follow", foreign_keys=[Follow.follower_id], back_populates="follower", cascade="all",
                                lazy="dynamic")
    followers = db.relationship("Follow", foreign_keys=[Follow.followed_id], back_populates="followed", cascade="all",
                                lazy="dynamic")
    # notifications
    notifications = db.relationship("Notification", back_populates="receiver", cascade="all")

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        # generate different size user's portraits.
        self.generate_avatar()
        # user follow self.
        self.follow(self)

    def generate_avatar(self):
        avatar = Identicon()
        filenames = avatar.generate(self.username)
        self.avatar_s = filenames[0]
        self.avatar_m = filenames[1]
        self.avatar_l = filenames[2]
        db.session.commit()

    def set_role(self):
        if self.role is None:
            if self.email == current_app.config["MAIL_DEFAULT_SENDER"]:
                # administrator have is not required to confirm identity data.
                self.role = Role.query.filter_by(name="Administrator").first()
                self.confirmed = True
            else:
                self.role = Role.query.filter_by(name="User").first()
            db.session.commit()

    # -------------------------------------------------------------------------------------------------------
    # password disposing
    @property
    def password(self):
        raise AttributeError

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # -------------------------------------------------------------------------------------------------------
    # User permission validated
    def can_permission(self, permission_data: int):
        return self.role.permission.data & permission_data == permission_data

    @property
    def is_admin(self):
        return self.can_permission(Permission.ADMINISTRATOR)

    # -------------------------------------------------------------------------------------------------------
    # User photo collected
    def collect(self, photo):
        if not self.is_collecting_photo(photo):
            collect = Collect(collector=self, collected=photo)
            db.session.add(collect)
            db.session.commit()

    def uncollected(self, photo):
        collect = Collect.query.with_parent(self).filter_by(collected_id=photo.id).first()
        if collect:
            db.session.delete(collect)
            db.session.commit()

    def is_collecting_photo(self, photo):
        return Collect.query.with_parent(self).filter_by(collected_id=photo.id).first() is not None

    # following methods
    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower=self, followed=user)
            db.session.add(follow)
            db.session.commit()

    def unfollow(self, user):
        follow = self.following.filter_by(followed=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()

    def is_following(self, user):
        """To check if  the user is followed by me"""
        if user.id is None:
            # The user data not submit to database,the method immediately return False.
            return False
        return self.following.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        """To check if user followed me"""
        return self.followers.filter_by(follower_id=user.id).first() is not None


# Many to Many relation with User. # not use now.
# roles_permissions = db.Table("roles_permissions",
#                              db.Column("role_id", db.Integer, db.ForeignKey("role.id")),
#                              db.Column("permission_id", db.Integer, db.ForeignKey("permission.id")))
#

# Rule model relationship with User.
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    permission_id = db.Column(db.Integer, db.ForeignKey("permission.id"))

    permission = db.relationship("Permission", back_populates="roles", uselist=False)

    # user
    users = db.relationship("User", back_populates="role")

    # init default role
    @staticmethod
    def init_role():
        roles_mapper = dict(Locked=Permission.FOLLOW | Permission.COLLECT,
                            User=Permission.FOLLOW | Permission.COLLECT | Permission.COMMENT | Permission.UPLOAD,
                            Moderator=Permission.FOLLOW | Permission.COLLECT | Permission.COMMENT
                                      | Permission.UPLOAD | Permission.MODERATE,
                            Administrator=0xff)  # all permission

        for role_name, permission in roles_mapper.items():
            role = Role.query.filter_by(name=role_name).first()

            if not role:
                role = Role(name=role_name)
                role.permission = Permission(data=permission)
                db.session.add(role)
            permission = Permission.query.filter_by(data=permission).first()
            if not permission:
                permission = Permission(data=permission)
                db.session.add(permission)
            db.session.commit()


class Permission(db.Model):
    FOLLOW = 0x01
    COLLECT = 0x02
    COMMENT = 0x04
    UPLOAD = 0x08
    MODERATE = 0x10
    ADMINISTRATOR = 0x80

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Integer, unique=True)
    roles = db.relationship("Role", back_populates="permission")


# many to many
tagging = db.Table("tagging", db.Column("photo_id", db.Integer, db.ForeignKey("photo.id")),
                   db.Column("tag_id", db.Integer, db.ForeignKey("tag.id")))


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), index=True)
    photos = db.relationship("Photo", secondary=tagging, back_populates="tags")


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500))
    filename = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # relation user
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", back_populates="photos", uselist=False)
    # file name fields that are decided size
    filename_s = db.Column(db.String(64))
    filename_m = db.Column(db.String(64))
    # report flag count
    flag = db.Column(db.Integer, default=0)
    # tag of photo
    tags = db.relationship("Tag", secondary=tagging, back_populates="photos")
    # collectors are collected this
    collectors = db.relationship("Collect", back_populates="collected", cascade="all")
    # comments for this Photo
    can_comment = db.Column(db.Boolean, default=True)
    comments = db.relationship("Comments", back_populates="photo", cascade="all")

    def generate_different_size_photo(self):
        """if photo without other size format that generate these"""
        if not self.filename_s and not self.filename_m:
            f_path = os.path.join(current_app.config["UPLOAD_PATH"], self.filename)

            self.filename_s = resize_image(f_path, self.filename, 400)
            self.filename_m = resize_image(f_path, self.filename, 800)
            db.session.commit()


class Collect(db.Model):
    """User collected photos model"""
    collector_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    collected_id = db.Column(db.Integer, db.ForeignKey("photo.id"), primary_key=True)

    collector = db.relationship("User", back_populates="collections", lazy="joined")
    collected = db.relationship("Photo", back_populates="collectors", lazy="joined")

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", back_populates="comments", uselist=False)

    photo_id = db.Column(db.Integer, db.ForeignKey("photo.id"))
    photo = db.relationship("Photo", back_populates="comments", uselist=False)

    replied_id = db.Column(db.Integer, db.ForeignKey("comments.id"))
    # replied comment fields that self correlation
    replied = db.relationship("Comments", back_populates="replies", uselist=False, remote_side=[id])
    replies = db.relationship("Comments", back_populates="replied", cascade="all")

    # report flag
    flag = db.Column(db.Integer, default=0)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # relation ship
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    receiver = db.relationship("User", back_populates="notifications")


# Database Event
@db.event.listens_for(Photo, "after_delete", named=True)
def delete_photos(**kwargs):
    """delete image files by the path"""
    target = kwargs["target"]
    for filename in [target.filename, target.filename_s, target.filename_m]:
        path = os.path.join(current_app.config["UPLOAD_PATH"], filename)
        if os.path.exists(path):
            os.remove(path)  # delete file
