"""set flask config from env file"""
import os

database_url_formatting = r"postgresql://{user_name}:{password}@localhost/{database}"

with open("./.flaskenv", "r") as f:
    # import env variables
    for env_line in f.readlines():
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


class Production(DevConfig):
    DEBUG = False


config_dict = {"dev": DevConfig, "pro": Production}
