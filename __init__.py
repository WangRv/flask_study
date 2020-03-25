"""initialization flask app settings"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

from .settings import DevConfig


def create_app(config_object, name):
    app = Flask(name)
    app.config.from_object(config_object)
    db = SQLAlchemy(app)
    mail = Mail(app)
    Migrate(app, db)
    return app, db, mail


app, db, mail = create_app(DevConfig, "flask_study")


if __name__ == '__main__':
    app.run()
