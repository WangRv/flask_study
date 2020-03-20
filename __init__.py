"""initialization flask app settings"""
import importlib

from flask import Flask, url_for, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
# private settings
from .settings import config_dict

bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()
mail = Mail()


def create_app(config_object, name):
    app = Flask(name)
    app.config.from_object(config_object)
    registry_extension(app)
    registry_templates(app)
    registry_shell_context(app)
    # registry blue print
    registry_blueprints(app)

    return app


def registry_extension(app: Flask):
    db.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    Migrate(app, db)
    moment.init_app(app)


def registry_templates(app: Flask):
    @app.context_processor
    def make_template_variable():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.id).all()
        return dict(admin=admin, categories=categories)


def registry_blueprints(app: Flask):
    from .db_model import Post, Category,Comment
    globals()["Post"] = Post
    globals()["Category"] = Category
    globals()["Comment"] = Comment
    from .blueprints.auth_bp import auth_bp
    from .blueprints.blog_bp import blog_bp
    # registry blue print
    app.register_blueprint(auth_bp, url_prefix="/blog")
    app.register_blueprint(blog_bp, url_prefix="/blog")


def registry_shell_context(app: Flask):
    from .emails import test_send_email

    @app.shell_context_processor
    def make_shell_variable():
        return {"db": db, "app": app, "send": test_send_email}


def registry_errors(app: Flask):
    @app.errorhandler(403)
    def bad_request(e):
        return "403 Not found request"


dev = config_dict.get("dev")
app = create_app(dev, "flask_study")
from flask import current_app
from .db_model import *
from .forms import *
from .commands import *
from .views import *

if __name__ == '__main__':
    pass
