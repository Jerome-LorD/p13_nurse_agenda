"""Test agenda models module."""
# import unittest.mock as mock
from unittest.mock import patch

from dateutil.rrule import WEEKLY, rrule, SU
from dateutil.parser import *
from datetime import datetime, timedelta

from django.test import Client
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from nursapps.agenda.models import Event, Events
from nursapps.cabinet.models import Associate, Cabinet


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

        self.setup_events = Events.objects.create()

        self.total_visit_per_day = 1
        self.delta_visit_per_day = 1
        self.delta_visit_per_hour = 1
        self.number_of_days = 1
        self.name = "Client n1"
        self.care_address = "1 rue du chemin"
        self.cares = "AB, CD, EF"
        self.date = datetime(2021, 12, 31, 6, 0)

        self.event = Event()

        for i in range(
            0,
            self.total_visit_per_day * self.delta_visit_per_day,
            self.delta_visit_per_day,
        ):
            self.event = Event.objects.create(
                total_visit_per_day=self.total_visit_per_day,
                delta_visit_per_day=self.delta_visit_per_day,
                delta_visit_per_hour=self.delta_visit_per_hour,
                number_of_days=self.number_of_days,
                name=self.name,
                care_address=self.care_address,
                cares=self.cares,
                user_id=self.user.id,
                events_id=self.setup_events.id,
                date=self.date + timedelta(days=i),
            )

        associate = Associate.objects.filter(user_id=self.user.id).first()
        associates = Associate.objects.get_associates(associate.cabinet_id)
        self.all_events = Event.objects.filter(user_id__in=associates)

        self.group_event = Event.objects.filter(events_id=self.event.events_id)

        date_list = [
            datetime(2021, 12, 31, 6, 0),
        ]
        new_day, new_hour, new_minute = (31, 18, 0)
        self.updated_dates = Event.updated_date(
            date_list, new_day, new_hour, new_minute
        )

    def test_create_unique_day_at_unique_hour(self):
        """Test create unique day at unique hour."""
        event = Event.create_unique_day_at_unique_hour(self, user_id=self.user.id)

        self.assertEqual(event.date, self.date)

    def test_create_unique_day_with_recurence_in_it(self):
        """Test create unique day with recurence in it.

        Create two events: at 06:00 and 18:00 just one day
        The expected lenght is 2
        Expected results: datetime(2021, 12, 31, 6, 0) & datetime(2021, 12, 31, 18, 0)
        """
        self.total_visit_per_day = 2
        self.delta_visit_per_hour = 12
        self.date = datetime(2021, 12, 31, 6, 0)
        event = Event.create_unique_day_with_recurence_in_it(self, user_id=self.user.id)
        event = Event.objects.filter(events_id=event.events_id)
        self.assertTrue(len([event.date for event in event]) == 2)
        self.assertEqual(
            [
                datetime(2021, 12, 31, 6, 0),
                datetime(2021, 12, 31, 18, 0),
            ],
            [event.date for event in event],
        )

    def test_updated_date_with_unique_day_update_hour(self):
        """Test_updated_date."""
        date_list = [datetime(2021, 12, 31, 6, 0)]
        new_day, new_hour, new_minute = (31, 18, 0)
        upd_dt = Event.updated_date(date_list, new_day, new_hour, new_minute)
        expected = [datetime(2021, 12, 31, 18, 0)]
        self.assertEqual(upd_dt, expected)

    def test_updated_date_with_two_day_update_hours(self):
        """Test_updated_date two days."""
        date_list = [
            datetime(2021, 12, 31, 6, 0),
            datetime(2022, 1, 1, 6, 0),
            datetime(2022, 1, 2, 6, 0),
        ]
        new_day, new_hour, new_minute = (31, 18, 0)
        upd_dt = Event.updated_date(date_list, new_day, new_hour, new_minute)
        expected = [
            datetime(2021, 12, 31, 18, 0),
            datetime(2022, 1, 1, 18, 0),
            datetime(2022, 1, 2, 18, 0),
        ]
        self.assertEqual(upd_dt, expected)

    def test_updated_dates_in_group(self):
        """Test updated dates in group."""
        event = Event.updated_dates_in_group(
            self, group_event=self.group_event, updated_dates=self.updated_dates
        )

        self.assertEqual(event, self.updated_dates)

    def test_get_html_url(self):
        """Test get html url."""
        url = reverse(
            "nurse:edit_event",
            args=(
                self.event.date.strftime("%Y"),
                self.event.date.strftime("%m"),
                self.event.date.strftime("%d"),
                self.event.date.strftime("%H:%M"),
                self.event.id,
            ),
        )
        self.assertEquals(self.event.get_html_url, url)


class TestWeeklyEvent(TestCase):
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

        self.setup_events = Events.objects.create()

        total_visit_per_day = 3
        delta_visit_per_day = 1  # 1 for consecutives days (by default = 1)
        delta_visit_per_hour = 6
        day_per_week = "0, 2, 4"  # on monday, wednesday & friday
        number_of_days = 3
        name = "Client n4"
        care_address = "1 rue du chemin"
        cares = "AB, CD, EF"
        date = datetime(2022, 1, 3, 6, 0)

        def by_hour() -> tuple:
            ajust = 1
            return tuple(
                range(
                    date.hour,
                    (
                        (
                            delta_visit_per_hour + ajust
                            if delta_visit_per_hour > 3
                            else delta_visit_per_hour + ajust + 1
                        )
                        * total_visit_per_day
                    ),
                    delta_visit_per_hour,
                )
            )

        def by_week_day() -> tuple:
            """Return the rrule byweekday parameter."""
            return tuple([int(day_number) for day_number in day_per_week.split(", ")])

        dates = rrule(
            WEEKLY,
            count=number_of_days * total_visit_per_day,
            wkst=SU,
            byhour=by_hour(),
            byweekday=by_week_day(),
            dtstart=date,
        )
        dates = list(dates)

        self.events = Events.objects.create()

        for index in range(0, number_of_days * total_visit_per_day):
            Event.objects.create(
                total_visit_per_day=total_visit_per_day,
                delta_visit_per_day=delta_visit_per_day,
                delta_visit_per_hour=delta_visit_per_hour,
                number_of_days=number_of_days,
                name=name,
                care_address=care_address,
                cares=cares,
                user_id=self.user.id,
                day_per_week=day_per_week,
                events_id=self.events.id,
                date=dates[index],
            )
        self.all_events = Event.objects.filter(events_id=self.events.id).order_by(
            "date"
        )

        self.created_dates = [event.date for event in self.all_events]

    def test_create_weekly_event_with_delta_hour(self):
        """Test create weekly event with delta hour."""
        self.assertEqual(
            self.created_dates,
            [
                datetime(2022, 1, 3, 6, 0),
                datetime(2022, 1, 3, 12, 0),
                datetime(2022, 1, 3, 18, 0),
                datetime(2022, 1, 5, 6, 0),
                datetime(2022, 1, 5, 12, 0),
                datetime(2022, 1, 5, 18, 0),
                datetime(2022, 1, 7, 6, 0),
                datetime(2022, 1, 7, 12, 0),
                datetime(2022, 1, 7, 18, 0),
            ],
        )


class TestEventUnit(TestCase):
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

        self.setup_events = Events.objects.create()

        total_visit_per_day = 1
        delta_visit_per_day = 1
        delta_visit_per_hour = 6
        self.day_per_week = "0, 2, 4"  # on monday, wednesday & friday
        number_of_days = 1
        name = "Client n1"
        care_address = "1 rue du chemin"
        cares = "AB, CD, EF"
        date = datetime(2021, 12, 31, 6, 0)

        self.events = Events.objects.create()

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
                events_id=self.events.id,
                date=date + timedelta(days=i),
            )

    def test_get_dates(self):
        """Test get dates returns."""
        self.assertIsInstance(self.event.get_dates(), list)

    def test_get_recurency_dates(self):
        """Test get recurency dates."""
        self.assertIsInstance(self.event.get_recurency_dates(), list)

    def test_by_hour_returns_tuple(self):
        """Test by hour returns tuple."""
        self.assertIsInstance(self.event.by_hour(), tuple)

    def test_by_week_day_returns_tuple(self):
        """Test by week day returns tuple."""
        self.assertEqual(
            self.event.by_week_day(),
            tuple([int(day_number) for day_number in self.day_per_week.split(", ")]),
        )

    def test_updated_dates_in_group(self):
        """Test updated dates in group."""
