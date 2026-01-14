from bson import ObjectId
from fastapi import Depends, HTTPException, status

from src.utils.db import get_conn

from .jwt import decode_jwt
from .oauth2 import oauth2_scheme


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db=Depends(get_conn),
):
    token_data = decode_jwt(token)
    print(token_data.model_dump())

    user = await db.users.find_one({"_id": ObjectId(token_data.id)})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access",
        )

    return user


def require_role(role: str):
    async def checker(
        user=Depends(get_current_user),
    ):
        if user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden access",
            )
        return user

    return checker
