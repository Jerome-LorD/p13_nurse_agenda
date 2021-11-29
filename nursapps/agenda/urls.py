"""Urls agenda module."""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # path("<int:year>/<int:month>", views.home, name="home"),
    # path("accounts/profile/", views.create_cabinet, name="cabinet"),
    # path("accounts/profile/", views.ask_for_associate, name="ask_for"),
    # re_path(r"^autocomplete/", views.autocomplete, name="autocomplete"),
]
