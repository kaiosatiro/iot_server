import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import emails
from jinja2 import Template

from src.core.config import settings


@dataclass
class EmailData:
    html_content: str
    subject: str


logger = logging.getLogger("EMAIL Utils")


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    logger.info(f"Rendering template {template_name}")

    template_path = (
        Path(__file__).parent / "templates" / "build" / template_name
    ).read_text()
    html_content = Template(template_path).render(context)
    return html_content


def send_email(*, email_to: str, subject: str = "", html_content: str = "") -> None:
    logger.info("Sending email")
    if not settings.emails_enabled:
        logger.critical("no provided configuration for email variables")
        return

    logger.info("Preparing email")
    message = emails.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )

    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True

    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD

    logger.info(f"Sending email message")
    response = message.send(to=email_to, smtp=smtp_options)
    logger.info(f"Send email result code: {response.status_code} - {response.status_text}")


def generate_test_email(email_to: str) -> EmailData:
    logger.info("Generating test email")
    subject = f"{settings.PROJECT_NAME} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": settings.PROJECT_NAME, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: str, username: str, password: str
) -> EmailData:
    logger.info("Generating new account email")

    subject = f"{settings.PROJECT_NAME} - New account for user {username}"
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": settings.server_host,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(
    email_to: str, username: str, token: str
) -> EmailData:
    logger.info("Generating reset password email")

    subject = f"{settings.PROJECT_NAME} - Password recovery for user {username}"
    link = f"{settings.server_host}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)
