"""initialization flask app settings"""
# import path
import sys
from pathlib import Path

parent_dir = Path(__file__).parent.as_posix()
sys.path.insert(0, parent_dir)

from flask import Flask
from extension import db, moment, login_manager, migrate, ck_editor, bootstrap, mail, csrf
from settings import DevConfig


def create_app(config_object, name):
    app = Flask(name)
    app.config.from_object(config_object)
    # necessary initialization
    init_extension(app)
    init_blueprint(app)
    init_command(app)
    return app


def init_extension(app: Flask):
    db.init_app(app)
    migrate.init_app(app, db)
    ck_editor.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)


def init_blueprint(app: Flask):
    from blueprints.auth_bp import auth_bp
    from blueprints.main_bp import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)


def init_command(app: Flask):
    from commands import register_commands
    register_commands(app)


app = create_app(DevConfig, __name__)
# import db model

if __name__ == '__main__':
    app.run()
