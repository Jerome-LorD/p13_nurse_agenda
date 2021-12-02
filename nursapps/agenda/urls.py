"""Urls agenda module."""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sentry-debug/", views.trigger_error),
]
