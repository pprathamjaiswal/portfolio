"""
Email notification for new contact messages.

Design notes
------------
* **Never blocks the visitor.** SMTP handshakes take one to three seconds, and
  a slow or unreachable mail server must not make the form feel broken. The
  send runs on a background thread; the browser gets its response immediately.
* **Never loses a message.** The database row is written *before* this is
  called. If the email fails for any reason the message is still safe in the
  admin, and the failure is logged rather than raised.
* **Reply goes to the sender.** `Reply-To` is set to the visitor's address, so
  hitting Reply in your inbox answers them directly.
* **Off by default.** With no SMTP credentials configured nothing is sent and
  nothing breaks — the site runs exactly as before.
"""

from __future__ import annotations

import logging
import threading

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


def _truncate(text: str, limit: int = 120) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _send(contact_data: dict) -> None:
    """Build and deliver the notification. Runs on a background thread."""
    recipient = (settings.CONTACT_NOTIFY_EMAIL or "").strip()
    if not recipient:
        return

    context = {
        "name": contact_data["name"],
        "email": contact_data["email"],
        "message": contact_data["message"],
        "received_at": contact_data["received_at"],
        "site_url": settings.SITE_URL,
        "admin_url": f"{settings.SITE_URL}/admin/base/contact/",
    }

    subject = f"Portfolio enquiry from {contact_data['name']} — {_truncate(contact_data['message'], 60)}"

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=render_to_string("email/contact_notification.txt", context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
            # Reply in your mail client goes straight back to the visitor.
            reply_to=[contact_data["email"]],
        )
        email.attach_alternative(
            render_to_string("email/contact_notification.html", context), "text/html"
        )
        email.send(fail_silently=False)
        logger.info("Contact notification sent to %s", recipient)
    except Exception:
        # The message is already saved; a mail failure must never surface to
        # the visitor or crash the request.
        logger.exception("Could not send contact notification — the message is still saved")


def notify_new_contact(contact) -> None:
    """Fire off a notification for a saved Contact, without blocking."""
    if not settings.CONTACT_NOTIFY_EMAIL:
        return

    # Copy the fields out now: the model instance must not be touched from
    # another thread once the request's database connection closes.
    payload = {
        "name": contact.name,
        "email": contact.email,
        "message": contact.message,
        "received_at": timezone.localtime(contact.created_at or timezone.now()),
    }

    if getattr(settings, "CONTACT_NOTIFY_SYNC", False):
        # Tests and management commands want a deterministic, blocking send.
        _send(payload)
        return

    thread = threading.Thread(target=_send, args=(payload,), daemon=True)
    thread.start()
