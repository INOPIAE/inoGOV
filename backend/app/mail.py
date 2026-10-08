import logging
import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from app.config import settings

logger = logging.getLogger(__name__)

TEXTS = {
    "reset": (
        "Passwort zurücksetzen / Reset password",
        "Über diesen Link können Sie ein neues Passwort setzen (gültig {validity}):\n"
        "Use this link to set a new password (valid for {validity}):\n\n{link}\n",
    ),
    "invite": (
        "Einladung / Invitation",
        "Sie wurden eingeladen. Über diesen Link richten Sie Ihr Konto ein (gültig {validity}):\n"
        "You have been invited. Use this link to set up your account (valid for {validity}):\n\n{link}\n",
    ),
    "otp_reset": (
        "OTP neu einrichten / Set up OTP again",
        "Über diesen Link richten Sie Ihren OTP-Zugang neu ein (gültig {validity}):\n"
        "Use this link to set up your OTP again (valid for {validity}):\n\n{link}\n",
    ),
}
TEXTS["admin_reset"] = TEXTS["reset"]


def send_mail(to: str, subject: str, body: str) -> None:
    if not settings.smtp_server:
        logger.warning("SMTP nicht konfiguriert, Mail an %s\n%s\n\n%s", to, subject, body)
        return
    msg = EmailMessage()
    msg["From"] = formataddr((settings.smtp_from_name, settings.smtp_from_email))
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        # 465: TLS von Anfang an, 25: unverschlüsselt (lokaler Postfix), sonst STARTTLS (587)
        port = settings.smtp_port
        if port == 465:
            smtp = smtplib.SMTP_SSL(settings.smtp_server, port, timeout=10)
        else:
            smtp = smtplib.SMTP(settings.smtp_server, port, timeout=10)
        with smtp:
            if port not in (25, 465):
                smtp.starttls()
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(msg)
    except Exception:
        logger.exception("Mailversand an %s fehlgeschlagen", to)


def send_link_mail(kind: str, to: str, path: str, token: str, validity: str) -> None:
    subject, template = TEXTS[kind]
    link = f"{settings.frontend_url.rstrip('/')}{path}?token={token}"
    send_mail(to, f"{settings.app_name}: {subject}", template.format(link=link, validity=validity))
