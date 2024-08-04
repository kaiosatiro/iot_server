from sqlmodel import Session

from src import crud
from src.models import Device


class TestUserDeleteCascade:
    def test_user_delete_cascade(self, db: Session, messagesbatchfix) -> None:
        device_id, range_N = messagesbatchfix

        messages = crud.get_messages(db=db, device_id=device_id)
        assert len(messages) == 100, f"Should be the {range_N} 'set in the fixture'"

        device = db.get(Device, device_id)

        db.delete(device)
        db.commit()

        messages = crud.get_messages(db=db, device_id=device_id)
        assert len(messages) == 0, "Should be 0 messages"
