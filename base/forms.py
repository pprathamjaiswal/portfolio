"""Validation for the contact form."""

from __future__ import annotations

import re

from django import forms

from .models import Contact

NAME_RE = re.compile(r"^[A-Za-z][A-Za-z .'\-]{2,}$")
# Cheap check for obviously templated spam.
LINK_RE = re.compile(r"https?://|www\.", re.IGNORECASE)
MAX_LINKS = 2


class ContactForm(forms.ModelForm):
    # Honeypot: real people never see this field, bots fill it in.
    website = forms.CharField(required=False)

    class Meta:
        model = Contact
        fields = ["name", "email", "message"]

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if not NAME_RE.match(name):
            raise forms.ValidationError(
                "Please enter your name using letters only (at least 3 characters)."
            )
        return name

    def clean_email(self):
        return (self.cleaned_data.get("email") or "").strip().lower()

    def clean_message(self):
        message = (self.cleaned_data.get("message") or "").strip()
        if len(message) < 10:
            raise forms.ValidationError("Your message needs to be at least 10 characters.")
        if len(message) > 4000:
            raise forms.ValidationError("Your message is too long — please keep it under 4000 characters.")
        if len(LINK_RE.findall(message)) > MAX_LINKS:
            raise forms.ValidationError("Please remove some links from your message.")
        return message

    def clean(self):
        cleaned = super().clean()
        if (cleaned.get("website") or "").strip():
            # Honeypot tripped. Report a generic error; never explain why.
            raise forms.ValidationError("Your message could not be sent.")
        return cleaned

    def first_error(self) -> str:
        for errors in self.errors.values():
            if errors:
                return errors[0]
        return "Please check the form and try again."
