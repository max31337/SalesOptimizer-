import os
from functools import lru_cache
from .development import DevelopmentConfig
from .production import ProductionConfig
from .base import Environment

@lru_cache()
def get_settings():
    env = os.getenv("ENV", "development").lower()  # Change from ENVIRONMENT to ENV
    if env == "production":
        return ProductionConfig()
    return DevelopmentConfig()