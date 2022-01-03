"""Cabinet forms module."""
from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model

# from django.core.exceptions import ValidationError
from nursapps.cabinet.models import Cabinet


class CreateCabinet(forms.Form):  # CreateCabinetForm
    """New cabinet form."""

    cabinet = forms.CharField(
        max_length=240,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-user",
                "placeholder": "Votre nouveau cabinet",
                "id": "newcabinet",
            }
        ),
    )

    class Meta:
        """NewCabForm meta class."""

        model = Cabinet
        fields = "cabinet"


class SearchForCabinet(forms.Form):
    """New ask form."""

    search_for_cabinet = forms.CharField(
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
        fields = "search_for_cabinet"


class AssociationValidation(forms.Form):
    """New valid form."""

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

    def clean(self):
        confirm = self.cleaned_data["confirm"]
        if not confirm:
            raise forms.ValidationError("Il faut confirmer pour valider.")

    class Meta:
        """NewAskForm meta class."""

        model = Cabinet
        fields = ("confirm", "choice")
