from sqlalchemy.orm import Session

from src.core.database.db import Message, Device, Site, User


def create_test_data(session: Session):
    session.query(User).delete()
    session.query(Site).delete()
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
    site = Site(name="test_site", user_id=user.id)
    session.add(site)
    session.commit()
    for i in range(100):
        device = Device(name="{i}name", site_id=site.id, user_id=user.id)
        session.add(device)
    session.commit()
