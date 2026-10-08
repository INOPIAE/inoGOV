import smtplib

import pytest

from app import mail
from app.config import settings


class FakeSMTP:
    instances = []

    def __init__(self, host, port, timeout=None):
        self.kind = type(self).__name__
        self.host, self.port = host, port
        self.calls = []
        FakeSMTP.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def starttls(self):
        self.calls.append("starttls")

    def login(self, user, password):
        self.calls.append(("login", user))

    def send_message(self, msg):
        self.calls.append(("send", msg["From"], msg["To"]))


class FakeSMTPSSL(FakeSMTP):
    pass


@pytest.fixture
def smtp(monkeypatch):
    FakeSMTP.instances.clear()
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(smtplib, "SMTP_SSL", FakeSMTPSSL)
    monkeypatch.setattr(settings, "smtp_server", "smtp.example.com")
    monkeypatch.setattr(settings, "smtp_user", "user@example.com")
    monkeypatch.setattr(settings, "smtp_password", "pw")
    monkeypatch.setattr(settings, "smtp_from_email", "noreply@example.com")
    monkeypatch.setattr(settings, "smtp_from_name", "inoGOV")
    return FakeSMTP.instances


@pytest.mark.parametrize(
    "port, kind, starttls",
    [(465, "FakeSMTPSSL", False), (587, "FakeSMTP", True), (25, "FakeSMTP", False)],
)
def test_transport_depends_on_port(monkeypatch, smtp, port, kind, starttls):
    monkeypatch.setattr(settings, "smtp_port", port)
    mail.send_mail("a@example.com", "Betreff", "Text")
    (conn,) = smtp
    assert conn.kind == kind
    assert ("starttls" in conn.calls) is starttls
    assert ("login", "user@example.com") in conn.calls
    assert ("send", "inoGOV <noreply@example.com>", "a@example.com") in conn.calls


def test_send_failure_is_logged_not_raised(monkeypatch, smtp, caplog):
    def broken(*args, **kwargs):
        raise TimeoutError("timed out")

    monkeypatch.setattr(settings, "smtp_port", 465)
    monkeypatch.setattr(smtplib, "SMTP_SSL", broken)
    mail.send_mail("a@example.com", "Betreff", "Text")
    assert "fehlgeschlagen" in caplog.text


def test_no_server_only_logs(monkeypatch, caplog):
    monkeypatch.setattr(settings, "smtp_server", "")
    with caplog.at_level("WARNING"):
        mail.send_mail("a@example.com", "Betreff", "Text")
    assert "SMTP nicht konfiguriert" in caplog.text
