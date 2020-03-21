"""set flask config from env file"""
import os

database_url_formatting = r"postgresql://{user_name}:{password}@localhost/{database}"

with open(r"D:/flask_env/.flaskenv", "r") as f:
    # import env variables
    for env_line in f.readlines():
        if env_line.startswith("\n"):
            continue
        key, value = env_line.split("=")
        os.environ[key] = value.strip()


class BasicConfig:
    DEBUG: bool = False
    TESTING: bool = False
    DATABASE_URL: str = database_url_formatting.format(
        user_name=os.getenv("user_name"),
        password=os.getenv("password"),
        database=os.getenv("database"))


class DevConfig(BasicConfig):
    DEBUG = True
    SECRET_KEY: str = "My secret passphrase"
    SQLALCHEMY_DATABASE_URI = BasicConfig.DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # @todo Mail
    MAIL_SERVER: str = os.getenv("email_server")
    MAIL_PORT: int = int(os.getenv("email_port"))
    MAIL_PASSWORD: str = os.getenv("email_password")
    MAIL_USERNAME: str = os.getenv("email_username")
    MAIL_USE_SSL: bool = bool(os.getenv("email_ssl"))
    MAIL_DEFAULT_SENDER: str = os.getenv("email_default_sender")
    # @todo User
    ADMIN_EMAIL: str = os.getenv("blog_admin")

    # @todo Themes
    BLOG_THEMES: dict = eval(os.getenv("blog_themes"))


class Production(DevConfig):
    DEBUG = False


config_dict = {"dev": DevConfig, "pro": Production}
