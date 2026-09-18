"""
Send a sample contact notification so you can confirm email works.

    python manage.py testemail

Prints exactly which setting is wrong when it fails, instead of leaving you to
guess from an SMTP traceback.
"""

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from base.notifications import _send


class Command(BaseCommand):
    help = "Send a test contact-form notification to CONTACT_NOTIFY_EMAIL."

    def handle(self, *args, **options):
        ok = self.style.SUCCESS
        warn = self.style.WARNING
        bad = self.style.ERROR

        backend = settings.EMAIL_BACKEND.rsplit(".", 2)[-2]
        self.stdout.write("")
        self.stdout.write(f"  Backend      {backend}")
        self.stdout.write(f"  Host         {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        self.stdout.write(f"  Username     {settings.EMAIL_HOST_USER or '(not set)'}")
        self.stdout.write(
            f"  Password     {'set (' + str(len(settings.EMAIL_HOST_PASSWORD)) + ' chars)' if settings.EMAIL_HOST_PASSWORD else '(not set)'}"
        )
        self.stdout.write(f"  Sends to     {settings.CONTACT_NOTIFY_EMAIL or '(not set)'}")
        self.stdout.write("")

        if not settings.CONTACT_NOTIFY_EMAIL:
            self.stdout.write(bad("  CONTACT_NOTIFY_EMAIL is empty — set it in .env."))
            self.stdout.write("  Nothing was sent.\n")
            return

        if "console" in settings.EMAIL_BACKEND:
            self.stdout.write(
                warn(
                    "  EMAIL_HOST_USER is not set, so mail is printed here rather\n"
                    "  than sent. The message body follows:\n"
                )
            )

        if settings.EMAIL_HOST_PASSWORD and " " in settings.EMAIL_HOST_PASSWORD:
            self.stdout.write(
                warn(
                    "  Your app password contains spaces. Gmail displays it in\n"
                    "  four blocks, but it must be entered as 16 characters with\n"
                    "  no spaces.\n"
                )
            )

        try:
            _send(
                {
                    "name": "Test Recruiter",
                    "email": "recruiter@example.com",
                    "message": (
                        "This is a test message from your portfolio contact form.\n\n"
                        "If you are reading this in your inbox, notifications are "
                        "working correctly."
                    ),
                    "received_at": timezone.localtime(timezone.now()),
                }
            )
        except Exception as exc:  # pragma: no cover - diagnostics only
            self.stdout.write(bad(f"  Failed: {exc}"))
            return

        if "console" in settings.EMAIL_BACKEND:
            self.stdout.write(ok("\n  Rendered successfully (printed above, not sent)."))
        else:
            self.stdout.write(
                ok(f"  Sent. Check {settings.CONTACT_NOTIFY_EMAIL} (including spam).")
            )
            self.stdout.write(
                "  Nothing arrived? Check the server log — the send runs in the\n"
                "  background and logs the real error there.\n"
            )
