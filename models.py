from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash  # password security
from flask_login import UserMixin
from extension import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # user data
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
