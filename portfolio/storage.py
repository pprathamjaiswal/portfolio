"""Static file storage with a safer failure mode."""

from whitenoise.storage import CompressedManifestStaticFilesStorage


class ResilientManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """
    Manifest storage that does not take the whole site down over one file.

    Django's default manifest storage raises ``ValueError: Missing staticfiles
    manifest entry`` when a template references a file that is not in
    ``staticfiles.json``. That turns a stale manifest, or a single mistyped
    path, into a 500 on every page — catastrophic for a portfolio a recruiter
    is opening.

    With ``manifest_strict = False`` the reference falls back to the plain,
    unhashed URL instead. Worst case a single asset 404s; the page still
    renders.
    """

    manifest_strict = False
