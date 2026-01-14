from .base_model import CustomBaseModel


class Token(CustomBaseModel):
    access_token: str
    token_type: str


class TokenData(CustomBaseModel):
    id: str | None = None
    exp: int | None = None
    iat: int | None = None
