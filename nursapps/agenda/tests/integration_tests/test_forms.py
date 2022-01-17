"""Test agenda forms module."""
from dateutil.parser import *
from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client

from nursapps.agenda.forms import FormEvent, CARES_CHOICES
from nursapps.agenda.models import Event, Events
from nursapps.cabinet.models import Associate, Cabinet


User = get_user_model()


class TestFormEvent(TestCase):
    """Test FormEvent class."""

    def setUp(self):
        """Set Up."""
        self.user = User.objects.create_user(
            username="bill", email="bill@bool.com", password="poufpouf"
        )

        self.client = Client()

        cabinet = Cabinet.objects.create(name="cabbill")
        self.user.is_cabinet_owner = True
        self.user.save()
        Associate.objects.create(cabinet_id=cabinet.id, user_id=self.user.id)
        associate = Associate.objects.filter(user_id=self.user.id).first()

        associates = Associate.objects.get_associates(associate.cabinet_id)
        self.associates = [associate.id for associate in associates]

        self.setup_events = Events.objects.create()

        total_visit_per_day = 1
        delta_visit_per_day = 1
        delta_visit_per_hour = 0
        self.day_per_week = "0, 2, 4"  # on monday, wednesday & friday
        number_of_days = 1
        name = "Client n1"
        care_address = "1 rue du chemin"
        cares = "AB, CD, EF"
        date = datetime(2021, 12, 31, 6, 0)

        self.event = Event()

        for i in range(
            0,
            total_visit_per_day * delta_visit_per_day,
            delta_visit_per_day,
        ):
            self.event = Event.objects.create(
                total_visit_per_day=total_visit_per_day,
                delta_visit_per_day=delta_visit_per_day,
                delta_visit_per_hour=delta_visit_per_hour,
                day_per_week=self.day_per_week,
                number_of_days=number_of_days,
                name=name,
                care_address=care_address,
                cares=cares,
                user_id=self.user.id,
                events_id=self.setup_events.id,
                date=date + timedelta(days=i),
            )

    def test_form_event_name_field_placeholder(self):
        """Test form event name field placeholder."""
        form = FormEvent()
        self.assertTrue(
            form.fields["name"].label == ""
            and form.fields["name"].widget.attrs["placeholder"] == "Nom"
        )

    def test_form_event_care_address_field_placeholder(self):
        """Test form event care address field placeholder."""
        form = FormEvent()
        self.assertTrue(
            form.fields["name"].label == ""
            and form.fields["care_address"].widget.attrs["placeholder"] == "Adresse"
        )

    def test_form_event_cares_len_choices_equals_to_attrs_size(self):
        """Test form event cares len choices equals to attrs size."""
        form = FormEvent()
        self.assertEqual(
            str(len(CARES_CHOICES)), form.fields["cares"].widget.attrs["size"]
        )

    def test_form_event_date_input_format(self):
        """Test form event date input format."""
        form = FormEvent()
        self.assertEqual(form.fields["date"].input_formats, ("%d/%m/%Y %H:%M",))

    def test_form_event_total_visit_per_day_field_label(self):
        """Test form event total visit per day field label."""
        form = FormEvent()
        self.assertTrue(
            form.fields["total_visit_per_day"].label == None
            or form.fields["total_visit_per_day"].label
            == "Nombre de visites / jour --> 6h, 12h et 18h : 3 visites"
        )

    def test_form_event_delta_visit_per_hour_field_label(self):
        """Test form event delta visit per hour field label."""
        form = FormEvent()
        self.assertTrue(
            form.fields["delta_visit_per_hour"].label == None
            or form.fields["delta_visit_per_hour"].label
            == "Répétition toutes les x heures"
        )

    def test_form_event_delta_visit_per_day_field_label(self):
        """Test form event delta visit per day field label."""
        form = FormEvent()
        self.assertTrue(
            form.fields["delta_visit_per_day"].label == None
            or form.fields["delta_visit_per_day"].label == "Répétition tous les x jours"
        )

    def test_form_event_number_of_days_field_label(self):
        """Test form event number of days field label."""
        form = FormEvent()
        self.assertTrue(
            form.fields["number_of_days"].label == None
            or form.fields["number_of_days"].label == "Nombre total de jours"
        )
