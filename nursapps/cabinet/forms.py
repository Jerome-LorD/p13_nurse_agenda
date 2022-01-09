"""Cabinet forms module."""
from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model

# from django.core.exceptions import ValidationError
from nursapps.cabinet.models import Cabinet, RequestAssociate


class CreateCabinetForm(forms.Form):  # CreateCabinetForm
    """New cabinet form."""

    cabinet_name = forms.CharField(
        max_length=10,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-user",
                "placeholder": "Votre nouveau cabinet",
                "id": "newcabinet",
            }
        ),
        label="Nom de votre cabinet",
    )

    class Meta:
        """NewCabForm meta class."""

        model = Cabinet
        fields = "cabinet_name"


class SearchCabinetForm(forms.Form):
    """New ask form."""

    cabinet_name = forms.CharField(
        max_length=10,
        widget=forms.TextInput(
            attrs={
                "class": "form-control col-md-5",
                "placeholder": "nom du cabinet",
            }
        ),
        label="Demande d'association",
    )

    class Meta:
        """SearchCabinet meta class."""

        model = Cabinet
        fields = "cabinet_name"

    def clean_cabinet_name(self):
        """Clean_cabinet_name."""
        cabinet_name = self.cleaned_data["cabinet_name"]
        if not cabinet_name:
            raise forms.ValidationError("Une erreur.")
        return cabinet_name


class AssociationValidationForm(forms.Form):
    """Association validation form."""

    CHOICES = [("associate", "Associé(e)"), ("replacment", "Remplacant(e)")]

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
    choice = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)


class DeclineAssociationForm(forms.Form):
    """Decline association form."""

    decline = forms.CharField(
        label="",
        max_length=10,
        widget=forms.HiddenInput(
            attrs={
                "class": "form-control me-2",
                "id": "decline",
            }
        ),
    )

    def clean_decline(self):
        """Clean decline."""
        decline = self.cleaned_data["decline"]
        if not decline:
            raise forms.ValidationError("Une erreur.")
        return decline


class CancelAssociationForm(forms.Form):
    """Cancel association form."""

    cancel = forms.CharField(
        label="",
        max_length=10,
        widget=forms.HiddenInput(
            attrs={
                "class": "form-control me-2",
                "id": "cancel",
            }
        ),
    )

    def clean_cancel(self):
        """Clean confirm."""
        cancel = self.cleaned_data["cancel"]
        if not cancel:
            raise forms.ValidationError("Une erreur.")
        return cancel
