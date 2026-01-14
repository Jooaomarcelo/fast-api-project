from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.asynchronous.database import AsyncDatabase

from src.core.security.oauth2 import oauth2_scheme
from src.models.auth import Token
from src.models.user import UserCreate, UserOut
from src.services import auth_service
from src.utils.db import get_conn

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncDatabase = Depends(get_conn),
):
    access_token = await auth_service.authenticate_user(
        email=form_data.username,
        password=form_data.password,
        db=db,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/signup", response_model=UserOut)
async def signup(
    user: UserCreate,
    db: AsyncDatabase = Depends(get_conn),
):
    user_out = await auth_service.signup_user(user, db)
    return user_out


@router.get("/me", response_model=UserOut)
async def read_users_me(
    token: str = Depends(oauth2_scheme),
    db: AsyncDatabase = Depends(get_conn),
):
    return await auth_service.get_current_user(token, db)
