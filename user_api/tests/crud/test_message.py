from datetime import datetime, timedelta

import pytest
from sqlmodel import Session

from src import crud


class TestGetMessage:
    def test_get_all_message_by_device_id(self, db: Session, messagesbatchfix) -> None:
        device_id, range_N = messagesbatchfix
        messages = crud.get_messages(
            db=db,
            device_id=device_id,
            end_date=datetime.now() + timedelta(minutes=2)
        )

        assert len(messages) == 100, f"Should be the {range_N} 'set in the fixture'"
        assert messages[0].device_id == device_id, "Device id does not match"

    def test_get_empty_message_by_device_id(self, db: Session) -> None:
        messages = crud.get_messages(db=db, device_id=2)

        assert len(messages) == 0, "Messages not empty"

    def test_get_message_by_id(self, db: Session, messagesbatchfix) -> None:
        device_id, range_N = messagesbatchfix
        messages = crud.get_messages(
            db=db,
            device_id=device_id,
            end_date=datetime.now() + timedelta(minutes=2)
        )

        msg = messages[66]
        query = crud.get_message_by_id(db=db, message_id=msg.id)
        assert query.id == msg.id, "Message id does not match"

        msg = messages[77]
        query = crud.get_message_by_id(db=db, message_id=msg.id)
        assert query.id == msg.id, "Message id does not match"

    def test_get_message_by_period_of_day(self, db: Session, messagesbatchfix) -> None:
        device_id, range_N = messagesbatchfix
        messages = crud.get_messages(
            db=db,
            device_id=device_id,
            start_date=datetime.now() - timedelta(hours=24),
            end_date=datetime.now() + timedelta(hours=3)
        )

        assert len(messages) == 100, f"Should be the {range_N} 'set in the fixture'"

    def test_get_message_by_period_of_day_using_default(self, db: Session, messagesbatchfix) -> None:
        device_id, range_N = messagesbatchfix
        messages = crud.get_messages(
            db=db,
            device_id=device_id,
        )

        assert len(messages) == 100, f"Should be the {range_N} 'set in the fixture'"

    @pytest.mark.skip(reason="Strange behavior")
    def test_get_messages_by_period_of_hour(self, db: Session, messagesbatchfix) -> None:
        device_id, range_N = messagesbatchfix
        messages = crud.get_messages(
            db=db,
            device_id=device_id,
            start_date=datetime.now() - timedelta(hours=1),
            end_date=datetime.now() + timedelta(minutes=2)
        )

        assert len(messages) == 100, f"Should be the {range_N} 'set in the fixture'"

    def test_get_msg_with_limit(self, db: Session, messagesbatchfix) -> None:
        device_id, range_N = messagesbatchfix
        messages = crud.get_messages(
            db=db,
            device_id=device_id,
            start_date=datetime.now() - timedelta(hours=24),
            end_date=datetime.now() + timedelta(minutes=2),
            limit=range_N / 2
        )

        assert len(messages) == range_N / 2, f"Should be {range_N / 2} messages"

    def test_get_msg_with_limit_and_off_set(self, db: Session, messagesbatchfix) -> None:
        device_id, range_N = messagesbatchfix
        messages = crud.get_messages(
            db=db,
            device_id=device_id,
            start_date=datetime.now() - timedelta(hours=24),
            end_date=datetime.now() + timedelta(minutes=2),
            limit=range_N / 2,
            offset=range_N / 2
        )

        assert len(messages) == range_N / 2, f"Should be {range_N / 2} messages"

        messages = crud.get_messages(
            db=db,
            device_id=device_id,
            start_date=datetime.now() - timedelta(hours=24),
            end_date=datetime.now() + timedelta(minutes=2),
            limit=10,
            offset=60
        )

        assert len(messages) == 10, "Should be 10 messages"

    def test_get_msg_with_limit_and_off_set_out_of_range(self, db: Session, messagesbatchfix) -> None:
        device_id, range_N = messagesbatchfix
        messages = crud.get_messages(
            db=db,
            device_id=device_id,
            start_date=datetime.now() - timedelta(hours=24),
            end_date=datetime.now() + timedelta(minutes=2),
            limit=range_N / 2,
            offset=range_N
        )

        assert len(messages) == 0, "Should be 0 messages"

        messages = crud.get_messages(
            db=db,
            device_id=device_id,
            start_date=datetime.now() - timedelta(hours=24),
            end_date=datetime.now() + timedelta(minutes=2),
            limit=10,
            offset=range_N
        )

        assert len(messages) == 0, "Should be 0 messages"

    def test_get_msg_with_off_set(self, db: Session, messagesbatchfix) -> None:
        device_id, range_N = messagesbatchfix
        messages = crud.get_messages(
            db=db,
            device_id=device_id,
            start_date=datetime.now() - timedelta(hours=24),
            end_date=datetime.now() + timedelta(minutes=2),
            offset=60
        )

        assert len(messages) == 40, f"Should be {40} messages"


class TestDeleteMessage:
    def test_delete_msg_per_msg_id(self, db: Session, messagesbatchfix) -> None:
        device_id, range_N = messagesbatchfix
        messages = crud.get_messages(
            db=db,
            device_id=device_id,
            end_date=datetime.now() + timedelta(minutes=2)
        )

        assert len(messages) == 100, f"Should be the {range_N} 'set in the fixture'"

        msgA = messages[66]
        query = crud.get_message_by_id(db=db, message_id=msgA.id)
        assert query.id == msgA.id, "Message id does not match"
        crud.delete_message(db=db, message=query)
        query = crud.get_message_by_id(db=db, message_id=msgA.id)
        assert query is None, "Message not deleted"

        msgB = messages[77]
        query = crud.get_message_by_id(db=db, message_id=msgB.id)
        assert query.id == msgB.id, "Message id does not match"
        crud.delete_message(db=db, message=query)
        query = crud.get_message_by_id(db=db, message_id=msgB.id)
        assert query is None, "Message not deleted"

        messages = crud.get_messages(
            db=db,
            device_id=device_id,
            end_date=datetime.now() + timedelta(minutes=2)
        )
        assert len(messages) == 98, f"Should be the {range_N - 2} 'set in the fixture' minus the 2 deleted"

    def test_delete_msg_per_message_list(self, db: Session, messagesbatchfix) -> None:
        device_id, range_N = messagesbatchfix
        messages = crud.get_messages(
            db=db,
            device_id=device_id,
            end_date=datetime.now() + timedelta(minutes=2)
        )

        assert len(messages) == 98, "Should be the 98, 2 deleted in the previous test"

        msg_list = [msg.id for msg in messages[50:75]]
        crud.delete_messages_list(db=db, message_ids=msg_list)

        messages = crud.get_messages(
            db=db,
            device_id=device_id,
            end_date=datetime.now() + timedelta(minutes=2)
        )

        assert len(messages) == 73, "Should be the 73, 2 deleted in the previous test plus the 25 deleted in this test"

    def test_delete_msg_per_period(self, db: Session, messagesbatchfix) -> None:
        device_id, range_N = messagesbatchfix
        messages = crud.get_messages(
            db=db,
            device_id=device_id,
            end_date=datetime.now() + timedelta(minutes=2)
        )

        assert len(messages) == 73, "Should be the 73, 27 deleted in the previous test"

        crud.delete_messages_by_period(
            db=db, device_id=device_id,
            start_date=datetime.now() - timedelta(hours=24),
            end_date=datetime.now() + timedelta(minutes=2)
        )

        messages = crud.get_messages(
            db=db,
            device_id=device_id,
            end_date=datetime.now() + timedelta(minutes=2)
        )

        assert len(messages) == 0, "Should be the 0, all deleted"


class TestMessageContent:
    def test_validate_if_message_content_is_a_JSON(self, db: Session, messagesbatchfix) -> None:
        device_id, range_N = messagesbatchfix
        messages = crud.get_messages(
            db=db,
            device_id=device_id,
            end_date=datetime.now() + timedelta(minutes=2)
        )

        assert len(messages) == 100, f"Should be the {range_N} 'set in the fixture'"
        for msg in messages:
            assert isinstance(msg.message, dict), "Message content is not a JSON"
