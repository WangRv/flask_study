"""initialization flask app settings"""

from flask import Flask
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


def registry_blueprints(app: Flask):
    from .blueprints.auth_bp import auth_bp
    app.register_blueprint(auth_bp)


def registry_templates(app: Flask):
    pass


def registry_shell_context(app: Flask):
    @app.shell_context_processor
    def make_shell_db():
        return {"db": db, "app": app}


def registry_errors(app: Flask):
    @app.errorhandler(400)
    def bad_request(e):
        return "400 Bad request"


dev = config_dict.get("dev")
app = create_app(dev, "flask_study")
from .db_model import *
from .forms import *
from .commands import forge
from .views import *

if __name__ == '__main__':
    pass
