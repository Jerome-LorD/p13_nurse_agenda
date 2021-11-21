"""Nursauth forms module."""
from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model
from nursapps.agenda.models import Cabinet


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


class NewCabForm(forms.Form):
    """New cabinet form."""

    cabinet = forms.CharField(
        max_length=240,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-user",
                "placeholder": "Votre nouveau cabinet",
            }
        ),
    )

    class Meta:
        """NewCabForm meta class."""

        model = Cabinet
        fields = "cabinet"


class NewAskForm(forms.Form):
    """New ask form."""

    askfor = forms.CharField(
        max_length=140,
        widget=forms.TextInput(
            attrs={
                "class": "form-control col-md-2",
                "placeholder": "nom du cabinet",
            }
        ),
    )

    class Meta:
        """NewAskForm meta class."""

        model = Cabinet
        fields = "askfor"


class NewValidForm(forms.Form):
    """New valid form."""

    confirm = forms.CharField(
        label="",
        max_length=10,
        widget=forms.HiddenInput(
            attrs={
                "class": "form-control me-2",
                "id": "confirm",
            }
        ),
    )

    def clean(self):
        confirm = self.cleaned_data["confirm"]
        if not confirm:
            raise forms.ValidationError("Il faut confirmer pour valider.")

    class Meta:
        """NewAskForm meta class."""

        model = Cabinet
        fields = "confirm"
