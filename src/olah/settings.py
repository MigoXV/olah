from fastapi import Request

BASE_SETTINGS = False
if not BASE_SETTINGS:
    try:
        from pydantic import BaseSettings
        BASE_SETTINGS = True
    except ImportError:
        BASE_SETTINGS = False

if not BASE_SETTINGS:
    try:
        from pydantic_settings import BaseSettings
        BASE_SETTINGS = True
    except ImportError:
        BASE_SETTINGS = False

if not BASE_SETTINGS:
    raise Exception("Cannot import BaseSettings from pydantic or pydantic-settings")

from .configs import OlahConfig

class AppSettings(BaseSettings):
    # The address of the model controller.
    config: OlahConfig = OlahConfig()

def get_settings(request: Request) -> AppSettings:
    return request.app.state.app_settings