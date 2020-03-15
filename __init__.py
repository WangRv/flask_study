"""initialization flask app settings"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from .settings import DevConfig


def create_app(config_object, name):
    app = Flask(name)
    app.config.from_object(config_object)
    db = SQLAlchemy(app)
    bootstrap = Bootstrap(app)
    mail = Mail(app)
    Migrate(app, db)
    return app, db, mail, bootstrap


app, db, mail, bootstrap = create_app(DevConfig, "flask_study")
from .db_model import *
from .forms import *
from .views import *

if __name__ == '__main__':
    app.run()
