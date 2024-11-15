from fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas import settings
from app.schemas import userCreate
from app.schemas import userOut

from app.models import User

from app.utils.db_OMR import get_async_session
from app.utils.users import hash_password

user_router = APIRouter(prefix="/users")


@AuthJWT.load_config
def get_config():
    return settings()


@user_router.post("/register", response_model=userOut)
async def user_register(user: userCreate, session: AsyncSession = Depends(get_async_session)):
    hashed_password = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )
    session.add(new_user)
    try:
        await session.commit()
        await session.refresh(new_user)
        return new_user
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该邮箱已被注册")