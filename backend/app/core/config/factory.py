from typing import Union
from .development import DevelopmentConfig
from .production import ProductionConfig
import os

def get_settings() -> Union[DevelopmentConfig, ProductionConfig]:
    # Check if running on Railway
    is_railway = os.getenv('RAILWAY_ENVIRONMENT') is not None
    env = os.getenv("ENV", "development").lower()
    
    # If on Railway or env is production, use production config
    if is_railway or env == "production":
        return ProductionConfig()
    
    # Otherwise use development config
    return DevelopmentConfig()