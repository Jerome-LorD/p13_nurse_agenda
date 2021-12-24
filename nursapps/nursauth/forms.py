"""Nursauth forms module."""
from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model

# from nursapps.agenda.models import Cabinet


class UserCreationForm(auth_forms.UserCreationForm):
    """User creation form class."""

    class Meta(auth_forms.UserCreationForm.Meta):
        """User creation form meta class."""

        model = get_user_model()


class InscriptForm(auth_forms.UserCreationForm):
    """Inscription form."""

    email = forms.CharField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control form-control-user",
                "input_type": "email",
                "placeholder": "Votre Email",
            }
        ),
    )
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-user",
                "placeholder": "Pseudo",
            }
        ),
    )
    password1 = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-user",
                "placeholder": "***********",
                "input_type": "password",
            }
        ),
    )
    password2 = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-user",
                "placeholder": "***********",
                "input_type": "password",
            }
        ),
    )

    class Meta:
        """InscriptForm meta class."""

        model = get_user_model()
        fields = ("username", "email", "password1", "password2")  # "cabinetname",


class NewLoginForm(auth_forms.UserCreationForm):
    """Login form."""

    email = forms.EmailField(
        max_length=200,
        widget=forms.EmailInput(
            attrs={
                "name": "email",
                "class": "form-control form-control-user",
                "placeholder": "Email",
            }
        ),
    )

    password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-user",
                "placeholder": "Mot de passe",
            }
        ),
    )

    class Meta:
        """LoginForm meta class."""

        model = get_user_model()
        fields = ("email", "password")
