from functools import lru_cache
from typing import Type

from app.conf.settings.base_settings import Settings
from app.utils.logger import log


@lru_cache
def get_app_settings() -> Settings:
    return Settings()