from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from src.core.security.jwt import decode_jwt, sign_jwt
from src.core.security.password import get_password_hash, verify_password
from src.models.user import User, UserCreate
from src.utils.app_error import AppError
from src.utils.date_now import get_utc_now


async def authenticate_user(
    email: str,
    password: str,
    db: AsyncDatabase,
) -> str:
    user = await db.get_collection("users").find_one({"email": email})

    if not user or not verify_password(password, user["password"]):
        raise AppError(status_code=401, message="Invalid credentials")

    return sign_jwt({"id": str(user["_id"])})


async def get_current_user(token: str, db: AsyncDatabase):
    token_data = decode_jwt(token)

    if not token_data:
        raise AppError(status_code=401, message="Token invalid or expired")

    print(token_data.model_dump())

    user_id = token_data.id

    if not user_id:
        raise AppError(status_code=401, message="Invalid token")

    user = await db.get_collection("users").find_one({"_id": ObjectId(user_id)})
    if not user:
        raise AppError(status_code=401, message="User not found")

    return user


async def signup_user(user: UserCreate, db: AsyncDatabase):
    existing = await db.get_collection("users").find_one({"email": user.email})

    if existing:
        raise AppError(status_code=400, message="An error occurred during signup")

    if user.password != user.confirmation_password:
        raise AppError(status_code=400, message="Passwords do not match")

    user_db = User(
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        password=get_password_hash(user.password),
        role=user.role,
        created_at=get_utc_now(),
        updated_at=get_utc_now(),
    )

    res = await db.get_collection("users").insert_one(user_db.model_dump(mode="json"))

    created_user = await db.get_collection("users").find_one({"_id": res.inserted_id})

    return created_user
