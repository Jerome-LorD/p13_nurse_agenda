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

    def test_create_event_at_only_one_date_and_twice_a_day(self):
        """Test create event at only one date and twice a day.

        Expecting results: 2 datetime on 1/1/2022 at 06:00 and 18:00
        >>> d = datetime.datetime(2021, 12, 26, 6, 0)
        >>> d + timedelta(hours=0)
        datetime.datetime(2021, 12, 26, 6, 0)
        >>> d + timedelta(hours=12)
        datetime.datetime(2021, 12, 26, 18, 0)

        Explanation for the range(start, stop, step):
        We have to specify how long is the hour delta in the form.
        If We wanna space from 12 hours bitween two events, we just have to type "12" in
        the form field.
        start = 0 to include the selected hour
        stop = 1 * 12 to add 12 hours more (only one day)
        step = 12
        """
        total_visit_per_day = 2
        delta_visit_per_day = 1
        delta_visit_per_hour = 12
        number_of_days = 1
        name = "Client n2"
        care_address = "1 rue du chemin"
        cares = "AB, CD, EF"
        events_id = self.events.id
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
                events_id=events_id,
                date=date + timedelta(hours=i),
            )
        events = Event.objects.filter(events_id=events_id)

        dates = [event.date for event in events]
        self.assertEqual(
            [
                datetime(2021, 12, 31, 6, 0),
                datetime(2021, 12, 31, 18, 0),
            ],
            dates,
        )

    def test_update_event_at_only_one_date_and_twice_a_day(self):
        """Test update event at only one date and twice a day.

        So we have two events on 26/12:

        datetime.datetime(2021, 12, 26, 6, 0)
        datetime.datetime(2021, 12, 26, 18, 0)
        And the point is to change the first one from 6 a.m. to 7 a.m. and leave the
        last one as it is.
        """
        total_visit_per_day = 2
        delta_visit_per_day = 1
        delta_visit_per_hour = 12
        number_of_days = 1
        name = "Client n2"
        care_address = "1 rue du chemin"
        cares = "AB, CD, EF"
        events_id = self.events.id
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
                events_id=events_id,
                date=date + timedelta(hours=i),
            )
        event = Event.objects.filter(events_id=events_id, date=date).first()

        dates_grp_event = [date]
        updated_dates = Event.updated_date(
            dates_grp_event, new_day=0, new_hour=7, new_minute=0
        )

        for date in updated_dates:
            Event.objects.filter(pk=event.id).update(
                name=name,
                care_address=care_address,
                cares=cares,
                user_id=self.user.id,
                date=date,
            )

        self.assertIn(date, updated_dates)

    def test_create_three_consecutive_days_with_three_events_spaced_6_hours_apart(self):
        """Test create three consecutive days with three events spaced 6 hours apart."""
        total_visit_per_day = 3
        delta_visit_per_day = 1  # 1 for consecutives days
        delta_visit_per_hour = 6
        number_of_days = 3
        name = "Client n3"
        care_address = "1 rue du chemin"
        cares = "AB, CD, EF"
        events_id = self.events.id
        date = datetime(2021, 12, 31, 6, 0)

        dates = []
        for index in range(0, number_of_days):
            dates += [
                date + timedelta(hours=hour)
                for hour in range(
                    0,
                    (total_visit_per_day * delta_visit_per_hour),
                    delta_visit_per_hour,
                )
                if index + date.hour not in [0, 1, 2, 3, 4, 5, 24]
            ]
            date += timedelta(days=delta_visit_per_day)

        for index in range(0, len(dates)):
            Event.objects.create(
                total_visit_per_day=total_visit_per_day,
                delta_visit_per_day=delta_visit_per_day,
                delta_visit_per_hour=delta_visit_per_hour,
                number_of_days=number_of_days,
                name=name,
                care_address=care_address,
                cares=cares,
                user_id=self.user.id,
                events_id=events_id,
                date=dates[index],
            )
        events = Event.objects.filter(events_id=events_id)

        all_dates = [event.date for event in events]

        self.assertEqual(
            [
                datetime(2021, 12, 31, 6, 0),
                datetime(2021, 12, 31, 12, 0),
                datetime(2021, 12, 31, 18, 0),
                datetime(2022, 1, 1, 6, 0),
                datetime(2022, 1, 1, 12, 0),
                datetime(2022, 1, 1, 18, 0),
                datetime(2022, 1, 2, 6, 0),
                datetime(2022, 1, 2, 12, 0),
                datetime(2022, 1, 2, 18, 0),
            ],
            all_dates,
        )

    def test_create_weekly_event_with_delta_hour(self):
        """Create a weekly event with delta in hour.

        3 times by day, every 6 hours from 06:00
        on monday, wednesday & friday.

        Expected: 9 dates
            - 3 on 31/12/2021
            - 3 on 3/1/2022
            - 3 on 5/1/2022
        """
        total_visit_per_day = 3
        delta_visit_per_day = 1  # 1 for consecutives days (by default = 1)
        delta_visit_per_hour = 6
        day_per_week = "0, 2, 4"  # on monday, wednesday & friday
        number_of_days = 3
        name = "Client n4"
        care_address = "1 rue du chemin"
        cares = "AB, CD, EF"
        events_id = self.events.id
        date = datetime(2021, 12, 31, 6, 0)

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
                events_id=events_id,
                date=dates[index],
            )
        events = Event.objects.filter(events_id=events_id)

        created_dates = [event.date for event in events]

        self.assertEqual(
            [
                datetime(2021, 12, 31, 6, 0),
                datetime(2021, 12, 31, 12, 0),
                datetime(2021, 12, 31, 18, 0),
                datetime(2022, 1, 3, 6, 0),
                datetime(2022, 1, 3, 12, 0),
                datetime(2022, 1, 3, 18, 0),
                datetime(2022, 1, 5, 6, 0),
                datetime(2022, 1, 5, 12, 0),
                datetime(2022, 1, 5, 18, 0),
            ],
            created_dates,
        )

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
