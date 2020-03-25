"""initialization flask app settings"""

from flask import Flask
from flask_login import current_user

# private settings
from .extension_module import (
    bootstrap, moment, ck_editor, db, csrf, mail, login_manager, Migrate)
from .settings import config_dict


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
    ck_editor.init_app(app)


def registry_templates(app: Flask):
    from .db_model import Admin, Category, Comment
    @app.context_processor
    def make_template_variable():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.id).all()
        return dict(admin=admin, categories=categories)

    @app.context_processor
    def make_admin_variable():
        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(unread_comments=unread_comments)


def registry_blueprints(app: Flask):
    from .blueprints.auth_bp import auth_bp
    from .blueprints.blog_bp import blog_bp
    from .blueprints.admin_bp import admin_bp
    # registry blue print
    app.register_blueprint(auth_bp, url_prefix="/blog")
    app.register_blueprint(blog_bp, url_prefix="/blog")
    app.register_blueprint(admin_bp, url_prefix="/blog")


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

from .utils import *
# import index of web site
from .views import *

if __name__ == '__main__':
    pass
