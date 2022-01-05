"""Test agenda models module."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from nursapps.agenda.models import Event, Events
from nursapps.cabinet.models import Associate, Cabinet
from dateutil.rrule import WEEKLY, rrule, SU
from dateutil.parser import *
from datetime import datetime, timedelta
from django.test import Client


User = get_user_model()


class TestEvent(TestCase):
    """Test Event class."""

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

        self.events = Events.objects.create()

    def test_user_is_cabinet_owner(self):
        """Test if the current user is a cabinet owner."""
        self.assertTrue(self.user.is_cabinet_owner)

    def test_create_event_at_only_one_date_and_only_one_hour(self):
        """Test create event at only one date and only one hour."""
        total_visit_per_day = 1
        delta_visit_per_day = 1
        delta_visit_per_hour = 0
        number_of_days = 1
        name = "Client n1"
        care_address = "1 rue du chemin"
        cares = "AB, CD, EF"
        # events_id = self.events.id
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
                events_id=self.events.id,
                date=date + timedelta(days=i),
            )

        self.assertEqual(event.date, date)
        self.assertEqual(event.name, "Client n1")

    def test_update_event_at_only_one_date_and_only_one_hour(self):
        """Test update hour from onlyone event.

        Create 31/12/2021 06:00
        Update 31/12/2021 07:15
        """
        total_visit_per_day = 1
        delta_visit_per_day = 1
        delta_visit_per_hour = 0
        number_of_days = 1
        name = "Client n1"
        care_address = "1 rue du chemin"
        cares = "AB, CD, EF"
        # events_id = Events.objects.create()
        date = datetime(2021, 12, 31, 6, 0)

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
                events_id=self.events.id,
                date=date + timedelta(days=i),
            )

        dates_grp_event = [date]

        updated_dates = event.updated_date(
            dates_grp_event, new_day=0, new_hour=7, new_minute=15
        )

        for date in updated_dates:
            Event.objects.filter(pk=event.id).update(
                name=event.name,
                care_address=event.care_address,
                cares=event.cares,
                user_id=event.user.id,
                date=date,
            )

        self.assertIn(date, updated_dates)

    def test_wrong_url_leads_to_404_status_code(self):
        """Test wrong url leads to 404 html page."""
        response = self.client.get("/agenda/2022/01/10/rdv/08:00/edit/262/blabla")
        self.assertEqual(response.status_code, 404)

    def test_url_leads_to_302_status_code(self):
        """Test url leads to 3025) status code."""
        response = self.client.get("/agenda/2022/01/10/")
        self.assertEqual(response.status_code, 302)

    def test_url_leads_to_200_status_code(self):
        """Test url leads to 200 status code."""
        self.client.force_login(self.user)
        response = self.client.get("/agenda/2022/1/3/")
        self.assertEqual(response.status_code, 200)
