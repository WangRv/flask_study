from enum import Enum


class HttpMethods(Enum):
    post: str = "POST"
    get: str = "GET"


class Operations(Enum):
    CONFIRM: str = "confirm"
    REST_PASSWORD: str = "reset_password"
    CHANGE_EMAIL: str = "change-email"
