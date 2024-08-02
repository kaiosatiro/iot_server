import logging

from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

import src.api.dependencies as deps
from src.mail.utils import generate_test_email, send_email
from src.models import Message

router = APIRouter()


@router.post(
    "/test-email/",
    tags=["Admin"],
    dependencies=[Depends(deps.get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    For the admin to test email sending.
    """
    logger = logging.getLogger("GET utils/test-email")
    logger.info(f"Sending test email to {email_to}")

    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")
