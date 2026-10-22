# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Plain-text mail through an existing SMTP server (Phase 1: forgot password, job notifications).

PeriHub doesn't run a mail server; it relays through whatever SMTP_* in .env
points at. Stdlib smtplib only - one plain-text message per call, no queue or
retry: a failed send is logged and the caller carries on (a reset request must
answer the same whether or not mail went out, so it can't leak which emails
have accounts).
"""

import smtplib
import ssl
from email.message import EmailMessage

from .globals import log, public_url, smtp_from, smtp_host, smtp_password, smtp_port, smtp_security, smtp_user


def smtp_configured() -> bool:
    """A server to send through - enough for job notifications."""
    return bool(smtp_host and smtp_from)


def mail_enabled() -> bool:
    """Forgot password needs both a server to send through and a public URL to link to."""
    return smtp_configured() and bool(public_url)


def send_mail(to: str, subject: str, body: str) -> bool:
    """Sends one plain-text email; False (logged) if it couldn't be sent."""
    message = EmailMessage()
    message["From"] = smtp_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    try:
        if smtp_security == "ssl":
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, context=ssl.create_default_context(), timeout=15)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
        with server:
            if smtp_security == "starttls":
                server.starttls(context=ssl.create_default_context())
            if smtp_user:
                server.login(smtp_user, smtp_password)
            server.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        log.warning("mailer: could not send %r to %s: %s", subject, to, exc)
        return False
    return True
