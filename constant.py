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


class Permission(Enum):
    """User's permission by hex representing"""
    FOLLOW = 0x01
    COLLECT = 0x02
    COMMENT = 0x04
    UPLOAD = 0x08
    MODERATE = 0x10
    ADMINISTRATOR = 0x80

    @classmethod
    def anonymous_user(cls):
        return cls.FOLLOW.value | cls.COLLECT.value

    @classmethod
    def normal_user(cls):
        return cls.anonymous_user() | cls.COMMENT.value | cls.UPLOAD.value

    @classmethod
    def moderator_user(cls):
        return cls.normal_user() | cls.normal_user()

    @classmethod
    def administrator_user(cls):
        return 0xff


class QueryRule(Enum):
    unread: str = "unread"
    read: str = "read"


if __name__ == '__main__':
    print(Permission.administrator_user(), Permission.moderator_user(), Permission.anonymous_user())
