# encoding:UTF-8
# base config object
class Config:
    pass


# Product environment config
class ProdConfig(Config):
    pass


# Development environment config
class DevConfig(Config):
    pass


# map dict
config = {"dev": DevConfig(), "pro": ProdConfig()}
__all__ = ["config"]
