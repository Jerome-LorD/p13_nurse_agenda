"""Cabinet urls module."""
from django.urls import path, re_path
from nursapps.cabinet import views

app_name = "cabinet"

urlpatterns = [
    path("accounts/profile/new-cabinet/", views.create_new_cabinet, name="create"),
    path("accounts/profile/ask-for-associate/", views.ask_for_associate, name="askfor"),
    path(
        "accounts/profile/confirm-associate/",
        views.confirm_associate,
        name="confirm_associate",
    ),
    path(
        "accounts/profile/decline-associate/",
        views.decline_associate,
        name="decline_associate",
    ),
    path(
        "accounts/profile/cancel-associate-demand/",
        views.cancel_associate_demand,
        name="cancel_associate_demand",
    ),
    re_path(r"^autocomplete/", views.autocomplete, name="autocomplete"),
]
