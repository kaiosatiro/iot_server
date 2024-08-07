from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: int | None = None


class DefaultResponseMessage(BaseModel):
    message: str


class Device(BaseModel):
    device_id: int