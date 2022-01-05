"""Agenda form module."""
import datetime as dt
from django import forms
from django.forms import DateInput
from django.forms.widgets import Select

from nursapps.agenda.models import Event
from nursapps.cabinet.models import Associate

from django.core.exceptions import ValidationError
from datetime import datetime


CARES_CHOICES = [
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

EVENT_CHOICES = [
    ("thisone", "Cet événement seulement "),
    ("thisone_after", "Cet événement et les suivants "),
    ("allevent", "Tout le groupe d'événement "),
]


class FormEvent(forms.ModelForm):
    """Form Event class."""

    def __init__(self, *args, **kwargs):
        """Init."""
        self.user = kwargs.pop("user", None)
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
            "number_of_days",
            "day_per_week",
        ]

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nom",
                "label for": "",
                "id": "",
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
                "label for": "",
                "id": "",
            }
        ),
        label="",
        required=True,
    )
    cares = forms.MultipleChoiceField(
        choices=CARES_CHOICES,
        label="",
        widget=forms.SelectMultiple(
            attrs={
                "class": "custom-select",
                "size": "14",
            }
        ),
    )

    total_visit_per_day = forms.ChoiceField(
        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4")],
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "label for": "",
                "id": "",
            }
        ),
        label="Nombre de visites / jour --> 6h, 12h et 18h : 3 visites",
        required=False,
    )
    delta_visit_per_hour = forms.ChoiceField(
        choices=[(0, ""), (3, "3"), (4, "4"), (5, "5"), (6, "6"), (12, "12")],
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "label for": "",
                "id": "",
            }
        ),
        label="Répétition toutes les x heures",
        required=False,
    )
    delta_visit_per_day = forms.ChoiceField(
        choices=[
            (1, "1"),
            (2, "2"),
            (3, "3"),
            (4, "4"),
            (5, "5"),
            (6, "6"),
            (7, "7"),
            (8, "8"),
        ],
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "label for": "",
                "id": "",
            }
        ),
        label="Répétition tous les x jours",
        required=False,
    )
    number_of_days = forms.ChoiceField(
        choices=[
            (1, "1"),
            (2, "2"),
            (3, "3"),
            (4, "4"),
            (5, "5"),
            (6, "6"),
            (7, "7"),
            (8, "8"),
            (9, "9"),
            (10, "10"),
            (11, "11"),
            (12, "12"),
            (13, "13"),
            (14, "14"),
            (15, "15"),
        ],
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "label for": "",
                "id": "",
            }
        ),
        label="Nombre total de jours",
        required=True,
    )
    day_per_week = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-check day-per-week",
            }
        ),
        label="Sélectionnez les jours pour créer une récurrence hebdomadaire",
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

    def clean_date(self):
        """Return cleaned date to accept only minutes in [0, 15, 30, 45]."""
        if self.user:
            associate = Associate.objects.filter(user_id=self.user.id).first()
            associates = Associate.objects.get_associates(associate.cabinet_id)
            associates = [associate.id for associate in associates]
            dt_obj = datetime.strptime(self.initial["date"][:-6], "%Y-%m-%d")
            events = Event.objects.filter(
                date__contains=dt.date(
                    year=dt_obj.year, month=dt_obj.month, day=dt_obj.day
                ),
                user_id__in=associates,
            )

            date = self.cleaned_data["date"]

            if (
                (date not in [i.date for i in events])
                and date.minute in [0, 15, 30, 45]
                and date.hour in list(range(6, 23))
            ):
                return date
            raise ValidationError("Vous ne pouvez pas valider cette tranche horaire.")


class EditEventForm(FormEvent):
    """Edit event form."""

    choice_event_edit = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect(
            attrs={"class": "form-check-input", "disabled": False}
        ),
        label="Sélectionnez quel événement modifier",
        choices=EVENT_CHOICES,
    )
