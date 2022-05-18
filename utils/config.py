import os
from abc import ABC, abstractmethod

from mcdreforged.utils.serializer import Serializable
from ruamel import yaml
from typing import IO, Dict, List


class _Config(Serializable, ABC):
    @staticmethod
    @abstractmethod
    def get_file() -> str:
        return ''

    @staticmethod
    def _loader(stream: IO):
        return yaml.load(stream, Loader=yaml.Loader)

    def _dumper(self, stream: IO):
        yaml.round_trip_dump(self.serialize(), stream, allow_unicode=True, indent=4)

    @classmethod
    def load(cls):
        if not os.path.exists(cls.get_file()):
            cls.get_default().save()
            return cls.get_default()
        with open(cls.get_file(), "r", encoding="UTF-8") as fp:
            return cls.deserialize(cls._loader(fp))

    def save(self):
        with open(self.get_file(), "w", encoding="UTF-8") as fp:
            self._dumper(fp)


class Config(_Config):
    @staticmethod
    def get_file() -> str:
        return 'config.yml'

    token: str = ''
    role_msg_id: str = ''
    log_level: str = 'INFO'
    guild_id: str = ''
    rule_channel_id: str = ''
    github_events_api: str = ''
    last_event_id: int = 0
    update_channel: str = ''
    agree_role_id: int = 0
    emoji_to_role_id_map: Dict[str, int] = {}
    log_file: bool = False

    def set_last_event(self, event_id) -> None:
        self.last_event_id = event_id
        self.save()


class Cookies(_Config):
    @staticmethod
    def get_file() -> str:
        return 'cookies.yml'

    cookies: Dict[str, List[str]] = {}

    def add_cookie(self, user: str, cookie: str) -> bool:
        if user not in self.cookies:
            self.cookies[user] = []
        if cookie not in self.cookies[user]:
            self.cookies[user].append(cookie)
            self.save()
            return True
        return False
