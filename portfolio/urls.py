from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from base.sitemaps import StaticSitemap

sitemaps = {"static": StaticSitemap}

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("", include("base.urls")),
]

handler404 = "base.views.handler404"
handler500 = "base.views.handler500"
