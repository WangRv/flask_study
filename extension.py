"""initialize flask app extension..."""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()
moment = Moment()
login_manager = LoginManager()
ck_editor = CKEditor()
bootstrap = Bootstrap()
mail = Mail()
csrf = CSRFProtect()