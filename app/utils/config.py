import os

from dotenv import load_dotenv
from rich import print

load_dotenv()





class ConfigMeta(type):
    def __getattribute__(cls, name) -> str:
        if name == "db_url":
            if getattr(cls, "_db_url", "") == "":
                print("Initializing: {{db_url: value}}")
                db_url = os.getenv("DB_URL")
                cls._db_url = "" if db_url is None else db_url
            return cls._db_url
        return super().__getattribute__(name)


class Config(metaclass=ConfigMeta):
    _db_url = ""
