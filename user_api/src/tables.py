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


class DeviceType(BaseModel, table=True):
    name: str = Field(nullable=False)
    description: str | None = None

    devices: list["Device"] = Relationship(back_populates='type')


class Device(BaseModel, table=True):
    name: str
    model: str | None = None
    description: str | None = None

    type_id: int = Field(foreign_key="device_type.id", nullable=False)
    type: "DeviceType" = Relationship(back_populates='devices')

    site_id: int = Field(foreign_key="site.id", nullable=False)
    site: "Site" = Relationship(back_populates='devices')

    messages: list["Message"] = Relationship(back_populates='device')


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)  # index=False?
    message: str #nullable=False
    created_on: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sa.func.now()},
        nullable=False,
    )

    device_id: int = Field(
        foreign_key="device.id",
        nullable=False,
        index=True
        ) 
    device: "Device" = Relationship(back_populates='messages')


class Site(BaseModel, table=True):
    name: str = Field(nullable=False)
    description: str | None = None

    user_id: int = Field(foreign_key="user.id", nullable=False)
    user: "User" = Relationship(back_populates='sites')

    devices: list["Device"] = Relationship(back_populates='site')


class UserRoleLink(SQLModel, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    role_id: int | None = Field(default=None, foreign_key="role.id", primary_key=True)


class User(BaseModel, table=True):
    username: str #nullable=False
    email: str = Field(unique=True, index=True)
    # password_hash: str #nullable=False

    sites: list["Site"] = Relationship(back_populates='user')
    roles: list["Role"] = Relationship(back_populates='users', link_model=UserRoleLink)


class RolePermissionLink(SQLModel, table=True):
    role_id: int | None = Field(default=None, foreign_key="role.id", primary_key=True)
    permission_id: int | None = Field(default=None, foreign_key="permission.id", primary_key=True)


class Role(BaseModel, table=True):
    name: str = Field(nullable=False)
    description: str | None = None

    users: list["User"] = Relationship(back_populates='roles', link_model=UserRoleLink)
    permissions: list["Permission"] = Relationship(back_populates='roles', link_model=RolePermissionLink)


class Permission(BaseModel, table=True):
    name: str = Field(nullable=False)
    description: str | None = None

    roles: list["Role"] = Relationship(back_populates='permissions', link_model=RolePermissionLink)
