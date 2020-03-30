from enum import Enum


class HttpMethods(Enum):
    post: str = "POST"
    get: str = "GET"

    @classmethod
    def methods_to_list(cls):
        return [x.value for x in cls]


class Operations(Enum):
    CONFIRM: str = "confirm"
    REST_PASSWORD: str = "reset_password"
    CHANGE_EMAIL: str = "change-email"
