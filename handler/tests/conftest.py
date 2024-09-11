from sqlalchemy.orm import Session

from src.core.database.db import Message, Device, Environment, User


def create_test_data(session: Session):
    session.query(User).delete()
    session.query(Environment).delete()
    session.query(Device).delete()
    session.query(Message).delete()
    session.commit()
    user = User(
        email="mail@mail.com",
        username="test_user",
        hashed_password="test_password",
        is_active=True,
        is_superuser=False,
    )
    session.add(user)
    session.commit()
    environment = Environment(name="test_environment", owner_id=user.id)
    session.add(environment)
    session.commit()
    for i in range(100):
        device = Device(name="{i}name", environment_id=environment.id, owner_id=user.id)
        session.add(device)
    session.commit()
