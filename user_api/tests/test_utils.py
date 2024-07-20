from src.core.security import get_password_hash, verify_password


def test_get_password_hash():
    password = "password"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password), "Should be True"
    assert not verify_password("wrong_password", hashed_password), "Should be False"
