"""Nursauth urls module."""
from django.urls import path, re_path
from nursapps.nursauth import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("accounts/inscript/", views.inscript, name="inscript"),
    path(
        "accounts/login/",
        views.login,
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(
            template_name="registration/logout.html", next_page="/"
        ),
        name="user_logout",
    ),
    path("accounts/profile/", views.user_profile, name="profile"),
    path(
        "accounts/password_reset/",
        auth_views.PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "accounts/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "accounts/reset/done/",
        auth_views.PasswordResetCompleteView,
        name="password_reset_complete",
    ),
]
