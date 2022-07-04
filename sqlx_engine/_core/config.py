from pydantic import BaseConfig


class Config(BaseConfig):
    improved_error_log: bool = True


config = Config()
