from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("contact/", views.contact_submit, name="contact_submit"),
    path("api/github/repos/", views.github_repos, name="github_repos"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
]
