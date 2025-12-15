from app.core.config import settings
from authx import AuthX, AuthXConfig

config = AuthXConfig()
config.JWT_SECRET_KEY = settings.JWT_SECRET_KEY
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_ACCESS_COOKIE_NAME = "access_token"
config.JWT_COOKIE_CSRF_PROTECT = False

security = AuthX(config=config)
