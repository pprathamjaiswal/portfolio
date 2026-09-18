"""
Show which database Django is actually talking to, and what is in it.

    python manage.py dbcheck

Written for one specific confusion: if DATABASE_URL is not set, Django does not
complain — it quietly falls back to the local SQLite file. Every command then
"succeeds" while your cloud database stays empty. This prints where the data
really went.
"""

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

EXPECTED = [
    ("base_contact", "your contact form messages"),
    ("auth_user", "your admin login"),
    ("django_migrations", "record of applied migrations"),
    ("django_session", "keeps you logged into /admin"),
]


class Command(BaseCommand):
    help = "Report which database is in use and whether the tables exist."

    def handle(self, *args, **options):
        ok = self.style.SUCCESS
        warn = self.style.WARNING
        bad = self.style.ERROR

        db = settings.DATABASES["default"]
        engine = db["ENGINE"].rsplit(".", 1)[-1]
        is_pg = "postgresql" in db["ENGINE"]

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("  WHERE IS DJANGO WRITING?"))
        self.stdout.write("")

        if is_pg:
            self.stdout.write(ok("  Target      CLOUD POSTGRES (Neon)"))
            self.stdout.write(f"  Host        {db.get('HOST')}")
            self.stdout.write(f"  Database    {db.get('NAME')}")
            self.stdout.write(f"  User        {db.get('USER')}")
        else:
            self.stdout.write(warn(f"  Target      LOCAL FILE ({engine})"))
            self.stdout.write(f"  File        {db.get('NAME')}")
            self.stdout.write("")
            self.stdout.write(
                bad(
                    "  DATABASE_URL is NOT set in this terminal, so nothing you run\n"
                    "  here reaches Neon. Set it, then run migrate again:\n"
                )
            )
            self.stdout.write(
                '    Windows :  $env:DATABASE_URL="postgresql://...neon.tech/neondb?sslmode=require"'
            )
            self.stdout.write(
                '    Mac/Linux: export DATABASE_URL="postgresql://...neon.tech/neondb?sslmode=require"'
            )
            self.stdout.write("")

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("  CAN DJANGO CONNECT?"))
        self.stdout.write("")

        try:
            connection.ensure_connection()
            self.stdout.write(ok("  Connection  OK"))
        except Exception as exc:
            self.stdout.write(bad(f"  Connection  FAILED — {exc}"))
            self.stdout.write("")
            return

        names = set(connection.introspection.table_names())

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("  WHAT IS IN IT?"))
        self.stdout.write("")
        self.stdout.write(f"  {len(names)} tables found (expect 11 after a clean migrate)")
        self.stdout.write("")

        missing = False
        for table, purpose in EXPECTED:
            if table in names:
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                self.stdout.write(ok(f"  [found]   {table:20} {count:>4} rows   — {purpose}"))
            else:
                missing = True
                self.stdout.write(bad(f"  [MISSING] {table:20}          — {purpose}"))

        self.stdout.write("")
        if missing:
            self.stdout.write(bad("  Tables are missing. Run:  python manage.py migrate"))
        elif is_pg:
            self.stdout.write(ok("  Your Neon database is ready."))
        else:
            self.stdout.write(
                warn("  These tables are on your laptop, NOT in Neon. See the note above.")
            )
        self.stdout.write("")
