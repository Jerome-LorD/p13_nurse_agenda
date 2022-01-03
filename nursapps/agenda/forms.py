"""Agenda form module."""
import datetime as dt
from django import forms
from django.forms import DateInput

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


class formEvent(forms.ModelForm):
    """
    Récupérer l'event_id en bdd.

    Auto corriger les heures hors créneaux : 16:20 => 16:15 ou 16:18 => 16:30
    """

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
        choices=CARES_CHOICES,
        label="",
        widget=forms.SelectMultiple(
            attrs={
                "class": "custom-select",
                "size": "14",
            }
        ),
    )

    total_visit_per_day = forms.CharField(
        max_length=1,
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
                "placeholder": "Écart en heure entre 2 passages. Ex. 6 [toutes les 6 heures]",
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
    number_of_days = forms.CharField(
        max_length=2,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Pendant tant de jours",
                "label for": "bobrech",
                "id": "bobrech",
            }
        ),
        label="Nombre total de jours",
        required=False,
    )
    day_per_week = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-check day_per_week",
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
            (
                # f"{date.hour}:{date.minute}"
                # not in [f"{i.date.hour}:{i.date.minute}" for i in events]
                date
                not in [i.date for i in events]
            )
            and date.minute in [0, 15, 30, 45]
            and date.hour in list(range(6, 23))
            # TODO: et si le créneau est ce
        ):
            # breakpoint()
            return date
        # elif f"{date.hour}:{date.minute}" in [
        #     f"{i.date.hour}:{i.date.minute}"
        #     for i in events
        #     if i.user_id == self.user.id
        # ]:
        # elif date in [i.date for i in events if i.user_id == self.user.id]:
        #     # breakpoint()
        #     return date
        raise ValidationError("Vous ne pouvez pas valider cette tranche horaire.")


# from django.forms import Select


# class Select(Select):
#     def create_option(self, *args, **kwargs):
#         option = super().create_option(*args, **kwargs)
#         if not option.get("value"):
#             option["attrs"]["disabled"] = "disabled"

#         if option.get("value") == 2:
#             option["attrs"]["disabled"] = "disabled"
#         breakpoint()
#         return option


class EditEventForm(formEvent):
    """Edit event form."""

    choice_event_edit = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect(
            attrs={
                "class": "form-check-input",
            }
        ),
        label="Sélectionnez quel événement modifier",
        choices=EVENT_CHOICES,
    )
