"""Urls agenda module."""
from django.urls import path, re_path

from . import views

app_name = "nurse"

urlpatterns = [
    path("", views.index, name="index"),
    path("agenda/<int:year>/<int:month>/", views.agenda, name="main_agenda"),
    path(
        "agenda/<int:year>/<int:month>/<int:day>/",
        views.daily_agenda,
        name="daily_agenda",
    ),
    re_path(
        r"^agenda/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/rdv/(?P<hour>[0-9|:]{5})/new/$",
        views.create_events,
        name="new_event",
    ),
    re_path(
        r"^agenda/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/rdv/(?P<hour>[0-9|:]{5})/edit/(?P<event_id>\d+)/$",
        views.edit_event,
        name="edit_event",
    ),
    re_path(
        r"^agenda/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/rdv/(?P<hour>[0-9|:]{5})/edit/(?P<event_id>\d+)/del_event/$",
        views.delete_event,
        name="del_event",
    ),
    path("sentry-debug/", views.trigger_error),
]
