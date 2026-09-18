from django.contrib import admin
from django.utils.html import format_html

from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "short_message", "created_at", "reply")
    list_filter = ("created_at",)
    search_fields = ("name", "email", "message")
    readonly_fields = ("name", "email", "message", "created_at")
    date_hierarchy = "created_at"

    @admin.display(description="Message")
    def short_message(self, obj):
        text = obj.message or ""
        return text if len(text) <= 70 else f"{text[:70]}…"

    @admin.display(description="")
    def reply(self, obj):
        """One-click reply straight from the message list."""
        return format_html(
            '<a href="mailto:{}?subject={}">Reply</a>',
            obj.email,
            f"Re: your message via my portfolio",
        )

    def has_add_permission(self, request):
        return False
