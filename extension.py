"""initialize flask app extension..."""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from flask_login import LoginManager, AnonymousUserMixin
from flask_wtf import CSRFProtect
from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_dropzone import Dropzone
from flask_avatars import Avatars

db = SQLAlchemy()
migrate = Migrate()
moment = Moment()
login_manager = LoginManager()
ck_editor = CKEditor()
bootstrap = Bootstrap()
mail = Mail()
csrf = CSRFProtect()
drop_zone = Dropzone()
avatars = Avatars()


class Guest(AnonymousUserMixin):
    @property
    def is_admin(self):
        return False

    @staticmethod
    def can_permission(permission_name):
        """always return False """
        return False


LoginManager.anonymous_user = Guest
