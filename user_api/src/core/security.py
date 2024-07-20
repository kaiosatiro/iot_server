from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def get_password_hash(paswd:str) -> str:
    return pwd_context.hash(paswd)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
