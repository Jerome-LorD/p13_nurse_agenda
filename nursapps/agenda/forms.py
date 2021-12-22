"""Agenda form module."""
from django import forms
from django.forms import DateInput

from nursapps.agenda.models import Event


DATE_ERROR_MESSAGE = {
    "required": "This field is required",
    "invalid": "Enter a valid value",
}

CHOIX_SOINS = [
    ("AC", "Anti-coagulant"),
    ("ALIM", "Alimentation"),
    ("BS", "Bilan sanguin"),
    ("F", "Facturation"),
    ("GC", "Glycémie capilaire"),
    ("IM", "Intra-musculaire"),
    ("INJ", "Injection"),
    ("MÉDIC", "Médicaments"),
    ("PERF", "Perfusion"),
    ("PST", "Pensement"),
    ("Pilulier", "Pilulier"),
    ("Poche", "Poche"),
    ("SC", "Sous-cutanée"),
    ("Fils", "Fils"),
]

DAYS_CHOICES = [
    (0, "Lundi"),
    (1, "Mardi"),
    (2, "Mercredi"),
    (3, "Jeudi"),
    (4, "Vendredi"),
    (5, "Samedi"),
    (6, "Dimanche"),
]


class formEvent(forms.ModelForm):
    """
    Récupérer l'event_id en bdd.

    Auto corriger les heures hors créneaux : 16:20 => 16:15 ou 16:18 => 16:30
    """

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self.fields["date"].input_formats = ("%d/%m/%Y %H:%M",)

    class Meta:
        """Meta."""

        model = Event
        widgets = {
            "date": DateInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                },
            )
        }

        fields = [
            "name",
            "care_address",
            "cares",
            "date",
            "total_visit_per_day",
            "delta_visit_per_hour",
            "delta_visit_per_day",
            "days_number",
            "day_per_week",
        ]

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nom",
                "label for": "bobrech",
                "id": "bobrech",
            }
        ),
        label="",
        required=True,
    )
    care_address = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Adresse",
                "label for": "bobrech",
                "id": "bobrech",
            }
        ),
        label="",
        required=True,
    )
    cares = forms.MultipleChoiceField(
        choices=CHOIX_SOINS,
        label="",
        widget=forms.SelectMultiple(
            attrs={
                "class": "custom-select",
                "size": "14",
            }
        ),
    )

    total_visit_per_day = forms.CharField(
        max_length=2,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "nombre de visites / jour : le mardi à 10h et 16h (2 visites)",
                "label for": "bobrech",
                "id": "bobrech",
            }
        ),
        label="Nombre de visites / jour --> 6h, 12h et 18h : 3 visites",
        required=False,
    )
    delta_visit_per_hour = forms.CharField(
        max_length=2,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "delta en heure entre 2 passages. Ex. 2 [toutes les 2 heures]",
                "label for": "bobrech",
                "id": "bobrech",
            }
        ),
        label="répétition toutes les x heures",
        required=False,
    )
    delta_visit_per_day = forms.CharField(
        max_length=2,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "répétition tout les x jours",
                "label for": "bobrech",
                "id": "bobrech",
            }
        ),
        label="répétition tous les x jours",
        required=False,
    )
    days_number = forms.CharField(
        max_length=2,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "nombre de jours",
                "label for": "bobrech",
                "id": "bobrech",
            }
        ),
        label="nombre de jours",
        required=False,
    )
    day_per_week = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form form-check",
            }
        ),
        label="Sélectionnez les jours pour créer une récurrence",
        choices=DAYS_CHOICES,
    )

    def clean_cares(self):
        """Return cleaned cares."""
        cares = self.cleaned_data["cares"]
        cares = ", ".join(cares)
        return cares

    def clean_day_per_week(self):
        """Return cleaned day per week."""
        day_per_week = self.cleaned_data["day_per_week"]
        day_per_week = ", ".join(day_per_week)
        return day_per_week
