import os

database_url_formatting = r"postgresql://{user_name}:{password}@localhost/{database}"
base_dir = os.path.abspath(os.path.dirname(__file__))
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
        database="picture")


class DevConfig(BasicConfig):
    DEBUG = True
    SECRET_KEY: str = "My secret passphrase"
    SQLALCHEMY_DATABASE_URI = BasicConfig.DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER: str = os.getenv("email_server")
    MAIL_PORT: int = int(os.getenv("email_port"))
    MAIL_PASSWORD: str = os.getenv("email_password")
    MAIL_USERNAME: str = os.getenv("email_username")
    MAIL_USE_SSL: bool = bool(os.getenv("email_ssl"))
    MAIL_DEFAULT_SENDER: str = os.getenv("email_default_sender")
    # upload file settings
    DROPZONE_MAX_FILE_SIZE = 3  # 3MB
    DROPZONE_MAX_FILES = 30  # supporting maximum thirty files.
    DROPZONE_ALLOWED_FILE_TYPE = "image"
    DROPZONE_ENABLE_CSRF = True
    # privatization file size
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024
    # uploads path
    UPLOAD_PATH = os.path.join(base_dir, "uploads")
    # image size variable
    PHOTO_SIZE = {"small": 400, "medium": 800}
    PHOTO_SUFFIX = {PHOTO_SIZE["small"]: "_s", # photo file name
                    PHOTO_SIZE["medium"]: "_m"}
