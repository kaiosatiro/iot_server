from datetime import datetime

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel


class BaseModel(SQLModel):
    id: int = Field(primary_key=True, nullable=False)
    created_on: str = Field(
        default=None,
        sa_type=sa.TIMESTAMP(timezone=True),
        sa_column_kwargs={"server_default": sa.func.now()},
        nullable=False,
    )
    updated_on: str = Field(
        default=None,
        sa_type=sa.TIMESTAMP(timezone=True),
        sa_column_kwargs={"onupdate": sa.func.now(), "server_default": sa.func.now()},
    )


# --------------------------- DEVICE MODELS ----------------------------
class DeviceBase(SQLModel):
    name: str = Field(max_length=55)
    model: str | None = Field(default=None, max_length=85)
    type: str | None = Field(default=None, max_length=55)
    description: str | None = Field(default=None, max_length=255)

    token: str | None = Field(default=None, max_length=255)


class DeviceCreation(DeviceBase):
    user_id: int | None = None
    site_id: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Home humidity sensor",
                    "model": "300x humidity sensor",
                    "type": "sensor",
                    "description": "A humidity sensor for home use",
                    "site_id": 1234567,
                    "user_id": 12345,
                }
            ]
        }
    }


class DeviceUpdate(DeviceBase):
    site_id: int | None = None
    name: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Home humidity sensor",
                    "model": "300x humidity sensor",
                    "type": "sensor",
                    "description": "A humidity sensor for home use",
                    "site_id": 1234567,
                }
            ]
        }
    }


class DeviceResponse(DeviceBase):
    id: int
    user_id: int
    site_id: int
    token: str
    created_on: datetime
    updated_on: datetime | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1234567890,
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.SWIEkIwXWo2slD671P44qv4K57vx4a5MW6POyzL-FJg",
                    "name": "Home humidity sensor",
                    "model": "300x humidity sensor",
                    "type": "sensor",
                    "description": "A humidity sensor for home use",
                    "site_id": 1234567,
                    "user_id": 12345,
                    "created_on": "2024-07-12T15:00:00Z",
                    "updated_on": "2024-07-12T15:00:00Z",
                }
            ]
        }
    }


class DevicesListResponse(SQLModel):
    user_id: int
    username: str
    site_id: int | None = None
    site_name: str | None = None
    data: list["DeviceResponse"]
    count: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": 12345,
                    "username": "user",
                    "count": 1,
                    "data": [
                        {
                            "id": 1234567890,
                            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.SWIEkIwXWo2slD671P44qv4K57vx4a5MW6POyzL-FJg",
                            "name": "Home humidity sensor",
                            "model": "300x humidity sensor",
                            "type": "sensor",
                            "description": "A humidity sensor for home use",
                            "site_id": 1234567,
                            "user_id": 12345,
                            "created_on": "2024-07-12T15:00:00Z",
                            "updated_on": "2024-07-12T15:00:00Z",
                        }
                    ],
                }
            ]
        }
    }


class Device(DeviceBase, BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    user: "User" = Relationship(back_populates="devices")

    site_id: int = Field(foreign_key="site.id", nullable=False, ondelete="CASCADE")
    site: "Site" = Relationship(back_populates="devices")

    messages: list["Message"] = Relationship(
        back_populates="device", cascade_delete=True
    )


# --------------------------- MESSAGE MODELS ---------------------------
class MessageBase(SQLModel):
    message: dict
    device_id: int


class MessageCreation(MessageBase):
    pass


class MessageResponse(SQLModel):
    id: int
    inserted_on: datetime
    message: dict

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1234567890123456,
                    "inserted_on": "2024-07-12T15:00:00Z",
                    "message": {
                        "deviceId": 1234567890,
                        "sensorId": "humiditySensor01",
                        "timestamp": "2024-07-12T15:00:00Z",
                        "type": "humidity",
                        "unit": "percent",
                        "value": 45.2,
                    },
                }
            ]
        }
    }


class MessagesListResponse(SQLModel):
    device_id: int
    device_name: str
    count: int
    data: list["MessageResponse"]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "device_id": 1234567890,
                    "device_name": "Home humidity sensor",
                    "count": 1,
                    "data": [
                        {
                            "id": 1234567890123456,
                            "inserted_on": "2024-07-12T15:00:00Z",
                            "message": {
                                "deviceId": 1234567890,
                                "sensorId": "humiditySensor01",
                                "timestamp": "2024-07-12T15:00:00Z",
                                "type": "humidity",
                                "unit": "percent",
                                "value": 45.2,
                            },
                        }
                    ],
                }
            ]
        }
    }


ID_SEQUENCE_MSG = sa.Sequence("message_id_seq", start=1223372036854775, increment=3)


class Message(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.BigInteger,
            ID_SEQUENCE_MSG,
            primary_key=True,
            server_default=ID_SEQUENCE_MSG.next_value(),
        ),
    )
    message: dict = Field(nullable=False, sa_type=sa.JSON)
    inserted_on: str = Field(
        default=None,
        sa_type=sa.TIMESTAMP(timezone=True),
        sa_column_kwargs={"server_default": sa.func.now()},
        nullable=False,
    )

    device_id: int = Field(
        foreign_key="device.id", nullable=False, index=True, ondelete="CASCADE"
    )
    device: "Device" = Relationship(back_populates="messages")


# --------------------------- SITE MODELS ------------------------------
class SiteBase(SQLModel):
    name: str = Field(nullable=False)
    description: str | None = Field(default=None, max_length=255)


class SiteCreation(SiteBase):
    pass

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Home",
                    "description": "Home site",
                }
            ]
        }
    }


class SiteUpdate(SiteBase):
    name: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Home",
                    "description": "Home site",
                }
            ]
        }
    }


class SiteResponse(SiteBase):
    id: int
    created_on: datetime
    updated_on: datetime | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1234567,
                    "name": "Home",
                    "description": "Home site",
                    "created_on": "2024-07-12T15:00:00Z",
                    "updated_on": "2024-07-12T15:00:00Z",
                }
            ]
        }
    }


class SitesListResponse(SQLModel):
    user_id: int
    username: str
    count: int
    data: list["SiteResponse"]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": 12345,
                    "username": "user",
                    "count": 1,
                    "data": [
                        {
                            "id": 1234567,
                            "name": "Home",
                            "description": "Home site",
                            "created_on": "2024-07-12T15:00:00Z",
                            "updated_on": "2024-07-12T15:00:00Z",
                        }
                    ],
                }
            ]
        }
    }


class Site(SiteBase, BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    user: "User" = Relationship(back_populates="sites")

    devices: list["Device"] = Relationship(back_populates="site", cascade_delete=True)


# --------------------------- USER MODELS -----------------------------
class UserBase(SQLModel):
    username: str = Field(unique=True, max_length=50, index=True)
    email: str = Field(
        unique=True
    )  # TODO replace email str with EmailStr when sqlmodel supports it
    about: str | None = Field(default=None, max_length=255)
    is_active: bool = True
    is_superuser: bool = False


class UserCreation(UserBase):
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "user",
                    "email": "johndoe@mail.com",
                    "password": "password",
                    "about": "I am a user",
                    "is_superuser": False,
                }
            ]
        }
    }


class UserUpdate(UserBase):
    id: int | None = None
    username: str | None = None
    email: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 12345,
                    "username": "newusername",
                    "email": "newemail@email.com",
                    "about": "I am a user",
                    "is_superuser": True,
                }
            ]
        }
    }


class UserUpdateMe(SQLModel):
    username: str | None = None
    email: str | None = None
    about: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "newuser",
                    "email": "newemail@email.com",
                    "about": "I am a user",
                }
            ]
        }
    }


class UpdatePassword(SQLModel):
    current_password: str
    new_password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "current_password": "password",
                    "new_password": "new_password",
                }
            ]
        }
    }


class UserResponse(SQLModel):
    id: int
    username: str
    email: str
    about: str | None = None
    created_on: datetime
    updated_on: datetime | None = None
    is_active: bool

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 12345,
                    "username": "user",
                    "email": "johndoe@email.com",
                    "about": "I am a user",
                    "created_on": "2024-07-12T15:00:00Z",
                    "updated_on": "2024-07-12T15:00:00Z",
                    "is_active": True,
                }
            ]
        }
    }


class UsersListResponse(SQLModel):
    data: list["UserResponse"]
    count: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "count": 1,
                    "data": [
                        {
                            "id": 12345,
                            "username": "user",
                            "email": "johndoe@email.com",
                            "about": "I am a user",
                            "created_on": "2024-07-12T15:00:00Z",
                            "updated_on": "2024-07-12T15:00:00Z",
                            "is_active": True,
                        }
                    ],
                }
            ]
        }
    }


class User(UserBase, BaseModel, table=True):
    hashed_password: str

    devices: list["Device"] = Relationship(back_populates="user", cascade_delete=True)
    sites: list["Site"] = Relationship(back_populates="user", cascade_delete=True)
    # roles: list["Role"] = Relationship(back_populates='users', link_model=UserRoleLink)


# --------------------------- UTILS MODELS -----------------------------
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: int | None = None


class DefaultResponseMessage(SQLModel):
    message: str


class NewPassword(SQLModel):
    token: str
    new_password: str


# class UserRoleLink(SQLModel, table=True):
#     user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
#     role_id: int | None = Field(default=None, foreign_key="role.id", primary_key=True)


# class RolePermissionLink(SQLModel, table=True):
#     role_id: int | None = Field(default=None, foreign_key="role.id", primary_key=True)
#     permission_id: int | None = Field(default=None, foreign_key="permission.id", primary_key=True)


# class Role(BaseModel, table=True):
#     name: str = Field(nullable=False)
#     description: str | None = None

#     users: list["User"] = Relationship(back_populates='roles', link_model=UserRoleLink)
#     permissions: list["Permission"] = Relationship(back_populates='roles', link_model=RolePermissionLink)


# class Permission(BaseModel, table=True):
#     name: str = Field(nullable=False)
#     description: str | None = None

#     roles: list["Role"] = Relationship(back_populates='permissions', link_model=RolePermissionLink)


# if __name__ == "__main__":
#     from sqlmodel import create_engine, Session, select
#     from sqlmodel.pool import StaticPool
#     from datetime import datetime, timedelta

#     DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/app"

#     engine = create_engine(
#         DATABASE_URL, echo=True
#     )

#     SQLModel.metadata.drop_all(engine)
#     SQLModel.metadata.create_all(engine)
#     with Session(engine) as session:
#         session.exec(select(1))

#     engine = create_engine(
#         "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
#         , echo=True
#     )
#     SQLModel.metadata.create_all(engine)
#     with Session(engine) as session:
#         user_in = UserCreation(
#             email="email",
#             username="random_lower_string()",
#             password="random_lower_string()",
#             about="random_lower_string()",
#             )
#         user = User.model_validate(user_in, update={"hashed_password": "random_lower"})
#         session.add(user)
#         session.commit()
#         session.refresh(user)

#         site_in = SiteCreation(
#             name="random_lower_string()",
#             description="random_lower_string()",
#             )
#         site = Site.model_validate(site_in, update={"user_id": user.id})
#         session.add(site)
#         session.commit()
#         session.refresh(site)

#         device_in = DeviceCreation(
#             name="random_lower_string()",
#             model="random_lower_string()",
#             type="random_lower_string()",
#             description="random_lower_string()",
#             user_id=user.id,
#             site_id=site.id
#             )

#         device = Device.model_validate(device_in)
#         session.add(device)
#         session.commit()
#         session.refresh(device)

#         messages = []
#         for _ in range(3):
#             message = MessageCreation(message={
#                 "deviceId": "12345",
#                 "sensorId": "humiditySensor01",
#                 "timestamp": "2024-07-12T15:00:00Z",
#                 "type": "humidity",
#                 "unit": "percent",
#                 "value": 45.2
#                 },
#                 device_id=device.id)
#             message_in = Message.model_validate(message)
#             messages.append(message_in)

#         session.add_all(messages)
#         session.commit()

#         user = session.get(User, user.id)
#         print("*******")
#         print(user.id)
#         print("*******")
#         session.delete(user)
#         session.commit()

#         yesterday = datetime.now() - timedelta(hours=24)
#         now = datetime.now()
#         print("*******")
#         print(yesterday)
#         print(now)
#         print(sa.func.now())
#         print("*******")

#         statement = select(Message).where(
#             User.id == user.id)
#         session_messages = session.exec(statement).all()

#         statement = select(Message).where(
#             Message.created_on >= yesterday,
#             Message.created_on <= now
#         )
#         session_messages = session.exec(statement).all()
#         print(session_messages)

#         SQLModel.metadata.drop_all(engine)
#         statement = delete(Message)
#         resulta = session.exec(statement)

#         statement = delete(Device)
#         resultb = session.exec(statement)

#         statement = delete(Site)
#         resultc = session.exec(statement)

#         statement = delete(User)
#         resultd = session.exec(statement)

#         session.commit()
#         print(resulta.rowcount)
#         print(resultb.rowcount)
#         print(resultc.rowcount)
#         print(resultd.rowcount)
