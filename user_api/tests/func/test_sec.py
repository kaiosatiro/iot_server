from datetime import timedelta

# from jwt import DecodeError, ExpiredSignatureError
from src.core.security import create_access_token, get_password_hash, verify_password
from src.crud import authenticate_user


def test_get_password_hash():
    password = "password"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password), "Should be True"
    assert not verify_password("wrong_password", hashed_password), "Should be False"


# --------------------------------------------------------------------------------------
class TestVerifyPassword:
    def test_authenticate_user(self, db, superuserfix):
        username = superuserfix["username"]
        password = superuserfix["password"]

        user = authenticate_user(db=db, username=username, password=password)
        assert user, "Should exist"
        assert user.username == username, "Should be True"
        assert user.is_active, "Should be True"
        assert user.is_superuser, "Should be True"

    def test_authenticate_user_incorrect_password(self, db, superuserfix):
        username = superuserfix["username"]
        password = "incorrect"

        user = authenticate_user(db=db, username=username, password=password)
        assert not user, "Should be False"

    def test_authenticate_user_incorrect_username(self, db, superuserfix):
        username = "incorrect"
        password = superuserfix["password"]

        user = authenticate_user(db=db, username=username, password=password)
        assert not user, "Should be False"


# --------------------------------------------------------------------------------------
def test_create_access_token():
    subject = "test_subject"
    expires_delta = timedelta(minutes=30)
    token = create_access_token(subject, expires_delta)
    assert isinstance(token, str)
    assert len(token) > 0


# @pytest.skip("")
# def test_create_access_token():
#     subject = "user@example.com"
#     expires_delta = timedelta(minutes=30)
#     access_token = create_access_token(subject, expires_delta)
#     assert isinstance(access_token, str)


# @pytest.skip("")
# def test_invalid_access_token():
#     subject = "user@example.com"
#     expires_delta = timedelta(minutes=-30)
#     try:
#         create_access_token(subject, expires_delta)
#         assert False  # Should raise an exception
#     except (DecodeError, ExpiredSignatureError):
#         assert True
