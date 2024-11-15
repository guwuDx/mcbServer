from fastapi_jwt_auth import AuthJWT

from schemas import settings

@AuthJWT.load_config
def get_config():
    return settings()