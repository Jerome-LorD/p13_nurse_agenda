"""Test agenda models module."""
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

        total_visit_per_day = 1
        delta_visit_per_day = 1
        delta_visit_per_hour = 0
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
                number_of_days=number_of_days,
                name=name,
                care_address=care_address,
                cares=cares,
                user_id=self.user.id,
                events_id=self.setup_events.id,
                date=date + timedelta(days=i),
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

    def test_an_event_is_linked_to_a_group_id(self):
        """Test a single event is linked to a group ID.

        This group is named events.id from the Events class model.

        2nd test:
        With 2 benchs of tests:
            - a single event
            - a group of recurency events

        Can updating a single event change the other groups?
        """
        total_visit_per_day = 1
        delta_visit_per_day = 1
        delta_visit_per_hour = 0
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

        self.assertNotEqual(self.events.id, self.setup_events.id)
        self.assertEqual(self.events.id, event.events_id)
        self.assertTrue(isinstance(event, Event))
        self.assertEqual(
            event.__str__(),
            f"{self.user} - {name} - {care_address} - {cares} - {date} - {self.events}",
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
        events = Event.objects.filter(events_id=self.events.id).order_by("date")

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

    def test_create_event_at_only_one_date_and_only_one_hour(self):
        """Test create event at only one date and only one hour."""
        total_visit_per_day = 1
        delta_visit_per_day = 1
        delta_visit_per_hour = 0
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
        date = datetime(2021, 12, 31, 6, 0)

        self.events = Events.objects.create()

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
        """Test create event at only one date and twice a day."""
        total_visit_per_day = 2
        delta_visit_per_day = 1
        delta_visit_per_hour = 12
        number_of_days = 1
        name = "Client n2"
        care_address = "1 rue du chemin"
        cares = "AB, CD, EF"
        date = datetime(2021, 12, 31, 6, 0)

        self.events = Events.objects.create()

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
                events_id=self.events.id,
                date=date + timedelta(hours=i),
            )
        events = Event.objects.filter(events_id=self.events.id).order_by("date")

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
        self.events = Events.objects.create()

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
                events_id=self.events.id,
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

    def test_update_create_unique_day_with_recurence_in_it_and_change_all_hours(self):
        """Test update event at only one date and twice a day.

        So we have two events on 26/12:
        datetime.datetime(2021, 12, 26, 6, 0)
        datetime.datetime(2021, 12, 26, 18, 0)

        And the point is to change the group from 6 a.m. to 7 a.m.

        The user's choice for this to happen is "thisone_after", that is, from the date
        chosen until the end.
        And he just has to change the time from 6 to 7.

        expected results:
        datetime.datetime(2021, 12, 26, 7, 0)
        datetime.datetime(2021, 12, 26, 19, 0)
        """
        self.events = Events.objects.create()
        # create the event
        total_visit_per_day = 2
        delta_visit_per_day = 1
        delta_visit_per_hour = 12
        number_of_days = 1
        name = "Client n2"
        care_address = "12 rue du chemin"
        cares = "AB, CD, EFG"
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
        # get the event:
        group_event = Event.objects.filter(events_id=events_id).order_by("date")

        dates_grp_event = [
            evt.date
            for evt in group_event
            if evt.date >= datetime(date.year, date.month, date.day)
        ]

        updated_dates = Event.updated_date(
            dates_grp_event, new_day=0, new_hour=7, new_minute=0
        )

        associate = Associate.objects.filter(user_id=self.user.id).first()
        associates = Associate.objects.get_associates(associate.cabinet_id)
        all_events = Event.objects.filter(user_id__in=associates).order_by("date")

        for index, event in enumerate(group_event):
            if date.hour not in [0, 1, 2, 3, 4, 5] or date not in [
                event.date for event in all_events
            ]:
                Event.objects.filter(pk=event.id).update(
                    name=name,
                    care_address=care_address,
                    cares=cares,
                    user_id=self.user.id,
                    date=updated_dates[index],
                )
        # the updated group is now:
        new_group_event = Event.objects.filter(events_id=events_id).order_by("date")
        new_group_event = [event.date for event in new_group_event]

        self.assertEqual(new_group_event, updated_dates)

    def test_create_three_consecutive_days_with_three_events_spaced_6_hours_apart(self):
        """Test create three consecutive days with three events spaced 6 hours apart."""
        total_visit_per_day = 3
        delta_visit_per_day = 1  # 1 for consecutives days
        delta_visit_per_hour = 6
        number_of_days = 3
        name = "Client n3"
        care_address = "1 rue du chemin"
        cares = "AB, CD, EF"
        date = datetime(2021, 12, 31, 6, 0)

        self.events = Events.objects.create()

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
                name=name,
                care_address=care_address,
                cares=cares,
                user_id=self.user.id,
                events_id=self.events.id,
                date=dates[index],
            )
        events = Event.objects.filter(events_id=self.events.id).order_by("date")

        dates = [event.date for event in events]

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
            dates,
        )

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
