database_url_formatting = r"postgresql://{user_name}:{password}@hostname/{database}"


class BasicConfig:
    DEBUG: bool = False
    TESTING: bool = False
    DATABASE_URL: str = database_url_formatting.format(
        user_name="postgresql",
        password="19930403a",
        database="dev")


class DevConfig(BasicConfig):
    DEBUG = True
    SECRET_KEY: str = "My secret passphrase"
    SQLALCHEMY_DATABASE_URI = BasicConfig.DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
