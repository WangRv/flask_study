"""initialization flask app settings"""
import importlib

from flask import Flask, url_for, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_login import LoginManager
from flask_wtf.csrf import  CSRFProtect
# private settings
from .settings import config_dict

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
moment = Moment()
mail = Mail()
csrf = CSRFProtect()

def create_app(config_object, name):
    app = Flask(name, static_folder="static")
    app.config.from_object(config_object)
    registry_extension(app)
    registry_templates(app)
    registry_shell_context(app)
    # registry blue print
    registry_blueprints(app)
    registry_errors(app)
    return app


def registry_extension(app: Flask):
    db.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)
    moment.init_app(app)


def registry_templates(app: Flask):
    @app.context_processor
    def make_template_variable():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.id).all()
        return dict(admin=admin, categories=categories)


def registry_blueprints(app: Flask):
    from .db_model import Post, Category, Comment, Admin
    globals()["Post"] = Post
    globals()["Category"] = Category
    globals()["Comment"] = Comment
    globals()["Admin"] = Admin
    from .emails import send_new_comment_email, send_new_reply_email
    global send_new_reply_email, send_new_comment_email
    from .forms import AdminCommentForm, CommentForm, LoginForm
    globals()["AdminCommentForm"] = AdminCommentForm
    globals()["CommentForm"] = CommentForm
    globals()["LoginForm"] = LoginForm
    from .utils import redirect_back
    global redirect_back
    from .blueprints.auth_bp import auth_bp
    from .blueprints.blog_bp import blog_bp
    # registry blue print
    app.register_blueprint(auth_bp, url_prefix="/blog")
    app.register_blueprint(blog_bp, url_prefix="/blog")


def registry_shell_context(app: Flask):
    from .emails import test_send_email

    @app.shell_context_processor
    def make_shell_variable():
        return {"db": db, "app": app, "send": test_send_email, "admin": Admin}


def registry_errors(app: Flask):
    @app.errorhandler(404)
    def bad_request(e):
        return "404 Not found request"


dev = config_dict.get("dev")
app = create_app(dev, "flask_study")
from flask import current_app
from .db_model import *
from .forms import *
from .commands import *
from .emails import *
from .utils import *
from .views import *

if __name__ == '__main__':
    pass
