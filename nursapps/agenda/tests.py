"""Test agenda module."""
from django.test import TestCase
from django.contrib.auth.hashers import make_password

from django.contrib.auth import get_user_model
from nursapps.agenda.forms import formEvent
from nursapps.agenda.models import Event, Associate, Cabinet
from dateutil.rrule import WEEKLY, rrule, SU, MO, TU, WE, TH, FR, SA
from dateutil.parser import *
from datetime import datetime, timedelta

User = get_user_model()


class TestEvent(TestCase):
    """Test Event class."""

    def setUp(self):
        """Set Up."""
        self.user = User.objects.create_user(
            username="bill", email="bill@bool.com", password="poufpouf"
        )

        cabinet = Cabinet.objects.create(name="cabbill")
        self.user.is_cabinet_owner = True
        self.user.save()
        Associate.objects.create(cabinet_id=cabinet.id, user_id=self.user.id)
        associate = Associate.objects.filter(user_id=self.user.id).first()

        associates = Associate.objects.get_associates(associate.cabinet_id)
        self.associates = [associate.id for associate in associates]

    def test_user_is_cabinet_owner(self):
        """Test if the current user is a cabinet owner."""
        self.assertTrue(self.user.is_cabinet_owner)

    def test_create_event_at_only_one_date_and_only_one_hour(self):
        """Test create event at only one date and only one hour."""
        total_visit_per_day = 1
        delta_visit_per_day = 1
        delta_visit_per_hour = None
        number_of_days = 1
        name = "Client n1"
        care_address = "1 rue du chemin"
        cares = "AB, CD, EF"
        group_id = "123456789"
        date = datetime(2021, 12, 31, 6, 0)

        event = Event()

        for i in range(
            0,
            total_visit_per_day * delta_visit_per_day,
            delta_visit_per_day,
        ):
            event = Event.objects.create(
                total_visit_per_day=total_visit_per_day,
                delta_visit_per_day=delta_visit_per_day,
                delta_visit_per_hour=delta_visit_per_hour,
                number_of_days=number_of_days,
                name=name,
                care_address=care_address,
                cares=cares,
                user_id=self.user.id,
                group_id=group_id,
                date=date + timedelta(days=i),
            )

        self.assertEqual(event.date, date)

    def test_create_event_at_only_one_date_and_twice_a_day(self):
        """Test create event at only one date and twice a day."""
        total_visit_per_day = 2
        delta_visit_per_day = 1
        delta_visit_per_hour = 12
        number_of_days = 1
        name = "Client n2"
        care_address = "1 rue du chemin"
        cares = "AB, CD, EF"
        group_id = "123456789"
        date = datetime(2021, 12, 31, 6, 0)

        for i in range(
            0,
            total_visit_per_day * delta_visit_per_hour,
            delta_visit_per_hour,
        ):
            Event.objects.create(
                total_visit_per_day=total_visit_per_day,
                delta_visit_per_day=delta_visit_per_day,
                delta_visit_per_hour=delta_visit_per_hour,
                number_of_days=number_of_days,
                name=name,
                care_address=care_address,
                cares=cares,
                user_id=self.user.id,
                group_id=group_id,
                date=date + timedelta(hours=i),
            )
        events = Event.objects.filter(group_id=group_id)

        dates = [event.date for event in events]
        self.assertEqual(
            [
                datetime(2021, 12, 31, 6, 0),
                datetime(2021, 12, 31, 18, 0),
            ],
            dates,
        )
