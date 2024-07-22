from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship
import sqlalchemy as sa


class BaseModel(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    created_on: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sa.func.now()},
        nullable=False,
    )
    updated_on: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={"onupdate": sa.func.now(), "server_default": sa.func.now()},
    )


# --------------------------- DEVICE MODELS ----------------------------
class DeviceBase(SQLModel):
    name: str
    model: str | None = None
    type: str | None = None
    description: str | None = None


class DeviceCreate(DeviceBase):
    user_id: int
    site_id: int


class DeviceUpdate(DeviceBase):
    name: str | None = None


class Device(DeviceBase, BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id", nullable=False)
    user: "User" = Relationship(back_populates='devices')

    site_id: int = Field(foreign_key="site.id", nullable=False)
    site: "Site" = Relationship(back_populates='devices')

    messages: list["Message"] = Relationship(back_populates='device')


# --------------------------- MESSAGE MODELS ---------------------------
class MessageBase(SQLModel):
    message: str 
    device_id: int


class MessageCreate(MessageBase):
    pass


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, index=False)  # index=False?
    message: str #nullable=False
    created_on: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True), # timezone=True
        sa_column_kwargs={"server_default": sa.func.now()},
        nullable=False,
    )

    device_id: int = Field(
        foreign_key="device.id",
        nullable=False,
        index=True
        ) 
    device: "Device" = Relationship(back_populates='messages')


# --------------------------- SITE MODELS ------------------------------
class SiteBase(SQLModel):
    name: str = Field(nullable=False)
    description: str | None = None


class SiteCreate(SiteBase):
    pass


class SiteUpdate(SiteBase):
    name: str | None = None


class Site(SiteBase, BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id", nullable=False)
    user: "User" = Relationship(back_populates='sites')

    devices: list["Device"] = Relationship(back_populates='site')


# --------------------------- USER MODELS -----------------------------
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True) # TODO replace email str with EmailStr when sqlmodel supports it
    username: str
    about: str | None = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    email: str | None = None


class UpdatePassword(SQLModel):
    current_password: str
    new_password: str


class User(UserBase, BaseModel, table=True):
    hashed_password: str

    devices: list["Device"] = Relationship(back_populates='user')
    sites: list["Site"] = Relationship(back_populates='user')
    # roles: list["Role"] = Relationship(back_populates='users', link_model=UserRoleLink)



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


if __name__ == "__main__":
    from sqlmodel import create_engine, Session, select
    from sqlmodel.pool import StaticPool
    from datetime import datetime, timedelta

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        , echo=True
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user_in = UserCreate(
            email="random_email()",
            username="random_lower_string()",
            password="random_lower_string()",
            about="random_lower_string()",
            )
        user = User.model_validate(user_in, update={"hashed_password": "random_lower"})
        session.add(user)
        session.commit()
        session.refresh(user)
                
        site_in = SiteCreate(
            name="random_lower_string()",
            description="random_lower_string()",
            )
        site = Site.model_validate(site_in, update={"user_id": user.id})
        session.add(site)
        session.commit()
        session.refresh(site)

        device_in = DeviceCreate(
            name="random_lower_string()",
            model="random_lower_string()",
            type="random_lower_string()",
            description="random_lower_string()",           
            user_id=user.id, 
            site_id=site.id
            )
        
        device = Device.model_validate(device_in)
        session.add(device)
        session.commit()
        session.refresh(device)

        messages = []
        for _ in range(1):
            message = MessageCreate(message="random_lower_string()", device_id=device.id)
            message_in = Message.model_validate(message)
            messages.append(message_in)

        session.add_all(messages)
        session.commit()


        yesterday = datetime.now() - timedelta(hours=24)
        now = datetime.now() + timedelta(hours=24)
        print("*******")
        print(yesterday)
        print(now)
        print(sa.func.now())
        print("*******")

        # statement = select(Message).where(
        #     User.id == user.id)
        # session_messages = session.exec(statement).all()
        statement = select(Message).where(
            Message.created_on >= yesterday.strftime('%Y-%m-%d %H:%M:%S'), Message.created_on <= now.strftime('%Y-%m-%d %H:%M:%S')
        )
        session_messages = session.exec(statement).all()
        print(session_messages)



