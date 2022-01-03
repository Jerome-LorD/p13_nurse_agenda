"""Agenda models module."""
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from dateutil.rrule import WEEKLY, rrule, SU, MO, TU, WE, TH, FR, SA
from dateutil.parser import *
from datetime import datetime, timedelta
from django.core.management import utils
from django.core.management.utils import get_random_secret_key as random_group_id

UserModel = get_user_model()


class EventManager(models.Manager):
    """SubstitutesManager class."""

    def create(self, *args, **kwargs):
        """Create event."""
        return super().create(*args, **kwargs)


class Event(models.Model):
    """Event model class.

    NB: random_group_id pretend to be a unique id dedicated to a group of events.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    care_address = models.CharField(max_length=400)
    cares = models.CharField(max_length=100, blank=False)
    care_price = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField(
        null=True,
        blank=True,
    )
    group_id = models.CharField(default=random_group_id(), max_length=400)
    total_visit_per_day = models.IntegerField()
    delta_visit_per_day = models.IntegerField(default=1)
    delta_visit_per_hour = models.IntegerField(default=0)
    number_of_days = models.IntegerField()
    day_per_week = models.CharField(max_length=100, blank=True, null=True)

    objects = EventManager()

    def __str__(self) -> str:
        """Return str representation."""
        return f"{self.user} - {self.name} - {self.care_address} - {self.cares}\
 - {self.date} - {self.group_id}"

    def __lt__(self, other) -> bool:
        """Compare the instance date selected with the event date."""
        return self.date < other.date

    @property
    def get_html_url(self) -> str:
        """Get html url."""
        url = reverse(
            "nurse:edit_event",
            args=(
                self.date.strftime("%Y"),
                self.date.strftime("%m"),
                self.date.strftime("%d"),
                self.date.strftime("%H:%M"),
                self.id,
            ),
        )
        return f"{url}"

    @classmethod
    def updated_date(cls, date_list, new_day=0, new_hour=0, new_minute=0) -> list:
        """Return an updated list of date.

        List to handle the recursion per week with a recursion during the day.
        """
        date_list = sorted(date_list)
        # breakpoint()
        if date_list[0].day > new_day:
            new_day = date_list[0].day
        start_day = date_list[0].day
        start_hour = date_list[0].hour
        start_minute = date_list[0].minute
        new_date = []
        for date in date_list:
            date += timedelta(days=new_day - start_day)
            date += timedelta(hours=new_hour - start_hour)
            date += timedelta(minutes=new_minute - start_minute)
            new_date.append(date)
        return new_date

    def by_hour(self) -> tuple:
        """Return the rrule byhour parameter."""
        ajust = 1
        return tuple(
            range(
                int(self.date.hour),
                (
                    (
                        self.delta_visit_per_hour + ajust
                        if self.delta_visit_per_hour > 3
                        else self.delta_visit_per_hour + ajust + 1
                    )
                    * self.total_visit_per_day
                ),
                self.delta_visit_per_hour,
            )
        )

    def by_week_day(self) -> tuple:
        """Return the rrule byweekday parameter."""
        return tuple([int(day_number) for day_number in self.day_per_week.split(", ")])

    def create_weekly_event_with_delta_hour(self, user_id):
        """Create a weekly event with delta in hour."""
        dates = rrule(
            WEEKLY,
            count=self.number_of_days * self.total_visit_per_day,
            wkst=SU,
            byhour=self.by_hour(),
            byweekday=self.by_week_day(),
            dtstart=self.date,
        )
        dates = list(dates)
        for index in range(0, self.number_of_days * self.total_visit_per_day):
            Event.objects.create(
                total_visit_per_day=self.total_visit_per_day,
                delta_visit_per_day=self.delta_visit_per_day,
                delta_visit_per_hour=self.delta_visit_per_hour,
                number_of_days=self.number_of_days,
                name=self.name,
                care_address=self.care_address,
                cares=self.cares,
                user_id=user_id,
                day_per_week=self.day_per_week,
                group_id=self.group_id,
                date=dates[index],
            )

    def create_unique_event_per_day_with_week_recurrency(self, user_id):
        """create_unique event per day with week recurrency."""
        dates = rrule(
            WEEKLY,
            count=self.number_of_days,
            wkst=SU,
            byweekday=self.by_week_day(),
            dtstart=self.date,
        )
        dates = list(dates)

        for index in range(0, self.number_of_days):
            Event.objects.create(
                total_visit_per_day=self.total_visit_per_day,
                delta_visit_per_day=self.delta_visit_per_day,
                number_of_days=self.number_of_days,
                name=self.name,
                care_address=self.care_address,
                cares=self.cares,
                user_id=user_id,
                day_per_week=self.day_per_week,
                group_id=self.group_id,
                date=dates[index],
            )

    def create_unique_day_at_unique_hour(self, user_id):
        """Create an event once a day at a specific time."""
        Event.objects.create(
            total_visit_per_day=self.total_visit_per_day,
            delta_visit_per_day=self.delta_visit_per_day,
            delta_visit_per_hour=self.delta_visit_per_hour,
            number_of_days=self.number_of_days,
            name=self.name,
            care_address=self.care_address,
            cares=self.cares,
            user_id=user_id,
            group_id=self.group_id,
            date=self.date,
        )

    def create_unique_day_at_unique_hour_during_several_consecutive_days(self, user_id):
        """Create unique day at unique hour during several consecutive days.

        1 X per day (on consecutives days).
        """
        print("create 5")
        dates = self.get_dates()
        for index in range(0, self.number_of_days):
            Event.objects.create(
                total_visit_per_day=self.total_visit_per_day,
                delta_visit_per_day=self.delta_visit_per_day,
                delta_visit_per_hour=self.delta_visit_per_hour,
                number_of_days=self.number_of_days,
                name=self.name,
                care_address=self.care_address,
                cares=self.cares,
                user_id=user_id,
                group_id=self.group_id,
                date=dates[index],
            )

    def create_unique_day_with_recurence_in_it(self, user_id):
        """Create unique day with recurence in it."""
        for i in range(
            0,
            self.total_visit_per_day * self.delta_visit_per_hour,
            self.delta_visit_per_hour,
        ):
            Event.objects.create(
                total_visit_per_day=self.total_visit_per_day,
                delta_visit_per_day=self.delta_visit_per_day,
                delta_visit_per_hour=self.delta_visit_per_hour,
                number_of_days=self.number_of_days,
                name=self.name,
                care_address=self.care_address,
                cares=self.cares,
                user_id=user_id,
                group_id=self.group_id,
                date=self.date + timedelta(hours=i),
            )

    def create_unique_day_with_recurency_in_days_delta(self, user_id):
        """Create consecutive days with recurency in the day.

        Eg: For example, twice a day every three days for a total of 5 days.
        """
        dates = self.get_recurency_dates()
        for index in range(0, len(dates)):
            Event.objects.create(
                total_visit_per_day=self.total_visit_per_day,
                delta_visit_per_day=self.delta_visit_per_day,
                delta_visit_per_hour=self.delta_visit_per_hour,
                number_of_days=self.number_of_days,
                name=self.name,
                care_address=self.care_address,
                cares=self.cares,
                user_id=user_id,
                group_id=self.group_id,
                date=dates[index],
            )

    def create_several_times_a_day_for_several_days(self, user_id):
        """Create several times a day for several days."""
        print("2 x par jour pendant plusieurs jours")
        dates = self.get_recurency_dates()
        for index in range(0, len(dates)):
            Event.objects.create(
                total_visit_per_day=self.total_visit_per_day,
                delta_visit_per_day=self.delta_visit_per_day,
                delta_visit_per_hour=self.delta_visit_per_hour,
                number_of_days=self.number_of_days,
                name=self.name,
                care_address=self.care_address,
                cares=self.cares,
                user_id=user_id,
                group_id=self.group_id,
                date=dates[index],
            )

    def create_events(self, user_id):
        """Create events."""
        if self.day_per_week and self.delta_visit_per_hour:
            print("create 1")
            self.create_weekly_event_with_delta_hour(user_id)
            """2x/j++ le lun jeu et sam"""

        elif self.day_per_week and not self.delta_visit_per_hour:
            print("create 2")
            self.create_unique_event_per_day_with_week_recurrency(user_id)
            """1x/jour le lun jeu et sam"""
        elif (
            not self.day_per_week
            and not self.delta_visit_per_hour
            and self.number_of_days < 2
        ):
            print("create 3")
            self.create_unique_day_at_unique_hour(user_id)
        elif (
            not self.day_per_week
            and self.delta_visit_per_day
            and self.number_of_days == 1
        ):
            print("create 4")
            self.create_unique_day_with_recurency_in_days_delta(user_id)
            """create_multiple_times_a_day_for_a_single_day"""

        elif (
            not self.day_per_week
            and not self.delta_visit_per_hour
            and self.number_of_days > 1
        ):
            print("create 5")
            self.create_unique_day_at_unique_hour_during_several_consecutive_days(
                user_id
            )
        elif (
            not self.day_per_week
            and self.delta_visit_per_hour
            and self.number_of_days == 1
        ):
            print("create 6")
            self.create_unique_day_with_recurence_in_it(user_id)

        elif (
            not self.day_per_week
            and self.delta_visit_per_hour
            and self.delta_visit_per_day
            and self.number_of_days > 1
        ):
            print("create 7")
            self.create_several_times_a_day_for_several_days(user_id)

    def get_dates(self) -> list:
        """Return a date list."""
        dates = [self.date]
        for index in range(
            0,
            (
                self.number_of_days - 1
                if self.number_of_days >= 3
                else self.number_of_days
            )
            * self.delta_visit_per_day,
            self.delta_visit_per_day,
        ):
            self.date += timedelta(days=self.delta_visit_per_day)
            dates.append(self.date)
        return dates

    def get_recurency_dates(self) -> list:
        """Return a list of dates.

        These are repeated in a day at a frequency in hours between each. With also
        a recurrence of days which can be consecutive or spaced apart by several days.

        For example, twice a day every three days for a total of 5 days.
        """
        dates = []
        for index in range(0, self.number_of_days):
            dates += [
                self.date + timedelta(hours=hour)
                for hour in range(
                    0,
                    (self.total_visit_per_day * self.delta_visit_per_hour),
                    self.delta_visit_per_hour,
                )
                if index + self.date.hour not in [0, 1, 2, 3, 4, 5, 24]
            ]
            self.date += timedelta(days=self.delta_visit_per_day)
        return dates

    def updated_dates_in_group(self, group_event, updated_dates):
        """Upd."""
        for index, event in enumerate(group_event):
            Event.objects.filter(pk=event.id).update(
                name=self.name,
                care_address=self.care_address,
                cares=self.cares,
                user_id=self.user.id,
                date=updated_dates[index],
            )

    def update_events(self, group_event, edit_choice):
        """Update events."""
        edit_choice = "".join(edit_choice)

        if edit_choice == "thisone":
            dates_grp_event = [self.date]

        elif edit_choice == "thisone_after":
            dates_grp_event = [
                evt.date
                for evt in group_event
                if evt.date >= datetime(self.date.year, self.date.month, self.date.day)
            ]
            group_event = sorted(
                [
                    evt
                    for evt in group_event
                    if evt.date
                    >= datetime(self.date.year, self.date.month, self.date.day)
                ]
            )

        elif edit_choice == "allevent":
            dates_grp_event = [evt.date for evt in group_event]

        updated_dates = self.updated_date(
            dates_grp_event, self.date.day, self.date.hour, self.date.minute
        )

        if len(dates_grp_event) > 1 and edit_choice == "allevent":
            """Update all group"""
            self.updated_dates_in_group(group_event, updated_dates)

        elif edit_choice == "thisone_after" and len(dates_grp_event) > 1:
            """P2 - test update this one & after if selected days"""
            self.updated_dates_in_group(group_event, updated_dates)

        elif (
            edit_choice == "thisone"
            and self.delta_visit_per_hour > 0
            and self.delta_visit_per_day > 1
            and self.number_of_days > 1
            and self.total_visit_per_day > 1
        ):
            """
            update an event among a batch of events.
            eg: 2x/d & 1d/2 during three days
            Only the date selected will be updated.
            """
            event = Event.objects.filter(pk=self.id)
            event.update(
                name=self.name,
                care_address=self.care_address,
                cares=self.cares,
                user_id=self.user.id,
                date=self.date,
            )

        elif (
            self.number_of_days > 1
            and self.delta_visit_per_hour > 0
            and len(self.day_per_week.split(", ")) < 2
        ):
            self.updated_dates_in_group(group_event, updated_dates)

        elif (
            len(self.day_per_week.split(", ")) > 1
            and self.delta_visit_per_hour > 0
            and self.number_of_days > 1
            and len(updated_dates) > 1
        ):
            self.updated_dates_in_group(group_event, updated_dates)

        else:
            """Update only one event, alone."""
            for date in updated_dates:
                Event.objects.filter(pk=self.id).update(
                    name=self.name,
                    care_address=self.care_address,
                    cares=self.cares,
                    user_id=self.user.id,
                    date=date,
                )
