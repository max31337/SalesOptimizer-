from .factory import get_settings
from .base import BaseConfig
from .development import DevelopmentConfig
from .production import ProductionConfig

settings = get_settings()

__all__ = [
    'settings',
    'BaseConfig',
    'DevelopmentConfig',
    'ProductionConfig'
]