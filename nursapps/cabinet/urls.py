"""Cabinet urls module."""
from django.urls import path, re_path
from nursapps.cabinet import views

urlpatterns = [
    path("accounts/profile/new_cabinet/", views.create_new_cabinet, name="create"),
    path("accounts/profile/ask-for-associate/", views.ask_for_associate, name="askfor"),
    path(
        "accounts/profile/confirm_associate/",
        views.confirm_associate,
        name="confirm_associate",
    ),
    re_path(r"^autocomplete/", views.autocomplete, name="autocomplete"),
]
