"""Cabinet forms module."""
from django import forms
from django.core.exceptions import ValidationError


class CreateCabinetForm(forms.Form):
    """New cabinet form."""

    cabinet_name = forms.CharField(
        max_length=16,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-user",
                "placeholder": "Votre nouveau cabinet",
                "id": "newcabinet",
                "name": "cabinet_name",
            }
        ),
        label="Nom de votre cabinet",
        required=False,
    )

    def clean_cabinet_name(self):
        """Clean cabinet name."""
        data = self.cleaned_data["cabinet_name"]
        if not data:
            raise ValidationError(
                (
                    "Ce champ est obligatoire, merci de saisir "
                    "un nom de cabinet à rechercher."
                )
            )
        return data


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

    def clean_cabinet_name(self):
        """Clean cabinet name."""
        data = self.cleaned_data["cabinet_name"]
        if not data:
            raise ValidationError(
                (
                    "Ce champ est obligatoire, merci de saisir "
                    "un nom du cabinet avant de valider la demande."
                )
            )
        return data


class AssociationValidationForm(forms.Form):
    """Association validation form."""

    CHOICES = [
        ("associate", "Associé(e)"),
        ("collaborator", "Collaborateur(trice)"),
        # ("replacment", "Remplacant(e)"),
    ]

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
