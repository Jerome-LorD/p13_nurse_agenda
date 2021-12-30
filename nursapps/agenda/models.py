"""Agenda models module."""
import random

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from nursapps.nursauth.models import User
from django.urls import reverse
from dateutil.rrule import WEEKLY, rrule, SU, MO, TU, WE, TH, FR, SA
from dateutil.parser import *
from datetime import datetime, timedelta

UserModel = get_user_model()


class Cabinet(models.Model):
    """Cabinet assoc model."""

    name = models.CharField(max_length=240, unique=True, default=False, blank=True)

    def __str__(self) -> str:
        """Str representation."""
        return self.name

    class Meta:
        """Meta."""

        ordering = ["name"]


class AssociateManager(models.Manager):
    """Associate manager."""

    def get_associates(self, cabinet_id):
        """Get associates."""
        associate = self.all().filter(cabinet_id=cabinet_id)
        associates = User.objects.filter(id__in=[i.user_id for i in associate])
        return associates


class Associate(models.Model):
    """Stores the user and the company they are affiliated with."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cabinet = models.ForeignKey(Cabinet, on_delete=models.CASCADE)

    objects = AssociateManager()

    def __str__(self) -> str:
        """Str representation."""
        return f"{self.user} - {self.cabinet}"


class RequestAssociate(models.Model):
    """Request to associate the new user with the owner of the cabinet."""

    sender_id = models.CharField(max_length=10, default=False, blank=True)
    receiver_id = models.CharField(max_length=10, default=False, blank=True)
    cabinet_id = models.CharField(max_length=10, default=False, blank=True)


class EventManager(models.Manager):
    """SubstitutesManager class."""

    def create(self, *args, **kwargs):
        """Create event."""
        return super().create(*args, **kwargs)


def random_group_id():
    """Generate a random ID to identify a group of event."""
    return str(random.randint(1000, 1000000000))


class Event(models.Model):
    """Event model class."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    care_address = models.CharField(max_length=400)
    cares = models.CharField(max_length=100, blank=False)
    care_price = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField(
        null=True,
        blank=True,
    )
    group_id = models.CharField(default=random_group_id, max_length=400)
    total_visit_per_day = models.IntegerField()
    delta_visit_per_day = models.IntegerField(default=1)
    delta_visit_per_hour = models.IntegerField(blank=True, null=True)
    number_of_days = models.IntegerField()
    day_per_week = models.CharField(max_length=100, blank=True, null=True)

    objects = EventManager()

    def __str__(self) -> str:
        """Return str representation."""
        return f"{self.user} - {self.name} - {self.care_address} - {self.cares}\
 - {self.date} - {self.group_id}"

    @property
    def get_html_url(self):
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
        start_day = date_list[0].day
        start_hour = date_list[0].hour
        start_minute = date_list[0].minute
        new_date = []
        for date_in in date_list:
            date_in += timedelta(days=new_day - start_day)
            date_in += timedelta(hours=new_hour - start_hour)
            date_in += timedelta(minutes=new_minute - start_minute)
            new_date.append(date_in)
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
            count=self.number_of_days * 2,
            wkst=SU,
            byhour=self.by_hour(),
            byweekday=self.by_week_day(),
            dtstart=self.date,
        )
        dates = list(dates)
        for index in range(0, self.number_of_days * 2):
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
        for i in range(
            0,
            self.total_visit_per_day * self.delta_visit_per_day,
            self.delta_visit_per_day,
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
                date=self.date + timedelta(days=i),
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

    def unique_day_with_recurence_in_it(self, user_id):
        print("unique day with recurency in it.")
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

    def create_multiple_time_in_day_with_on_several_days(self, user_id):
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

        elif self.day_per_week and not self.delta_visit_per_hour:
            print("create 2")
            self.create_unique_event_per_day_with_week_recurrency(user_id)
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
            self.unique_day_with_recurence_in_it(user_id)

        elif (
            not self.day_per_week
            and self.delta_visit_per_hour
            and self.delta_visit_per_day
            and self.number_of_days > 1
        ):
            print("create 7")
            self.create_multiple_time_in_day_with_on_several_days(user_id)

    def get_dates(self) -> list:
        """Return a date list."""
        dates = [self.date]
        for index in list(
            range(
                0,
                (
                    self.number_of_days - 1
                    if self.number_of_days >= 3
                    else self.number_of_days
                )
                * self.delta_visit_per_day,
                self.delta_visit_per_day,
            )
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
                if i + self.date.hour not in [0, 1, 2, 3, 4, 5, 24]
            ]
            self.date += timedelta(days=self.delta_visit_per_day)
        return dates

    def update_events(self, group_event, edit_choice):
        """Update events."""
        edit_choice = "".join(edit_choice)

        # breakpoint()

        if edit_choice == "thisone":  # ok
            dates_grp_event = [self.date]
            # breakpoint()
            # group_event = [
            #     evt
            #     for evt in group_event
            #     if evt.date.day == self.date.day and evt.date.hour == self.date.hour
            # ]

        elif edit_choice == "thisone_after":  # ok
            dates_grp_event = [evt.date for evt in group_event if evt.date >= self.date]
            group_event = [event for event in group_event if event.date >= self.date]
        elif edit_choice == "allevent":  # ok
            dates_grp_event = [evt.date for evt in group_event]

        updated_dates = self.updated_date(
            dates_grp_event, self.date.day, self.date.hour, self.date.minute
        )

        # breakpoint()

        if (
            len(self.day_per_week.split(", ")) > 1
            and self.delta_visit_per_hour
            and self.number_of_days > 1
            and len(updated_dates) > 1
        ):
            # Update a unique day and a group of days [with recurency].
            print("upd 1")
            for index, event in enumerate(group_event):
                Event.objects.filter(pk=event.id).update(
                    name=self.name,
                    care_address=self.care_address,
                    cares=self.cares,
                    user_id=self.user.id,
                    date=updated_dates[index],
                )

        elif (
            len(self.day_per_week.split(", ")) > 1
            and self.delta_visit_per_hour
            and self.number_of_days > 1
            and len(updated_dates) == 1
        ):
            # Updates an event that is part of a group in a day.
            # This day is part of a group of selected days.
            print("upd 1 unique")
            for date in updated_dates:
                Event.objects.filter(pk=self.id).update(
                    name=self.name,
                    care_address=self.care_address,
                    cares=self.cares,
                    user_id=self.user.id,
                    date=date,
                )

        elif (
            not self.day_per_week
            and not self.delta_visit_per_hour
            and self.number_of_days >= 1
        ):
            print("upd 2")
            # Updates an event that can be unique or that can be part of a group of
            # consecutive days // hum: or spaced by a date delta. (not sure)
            # Only once a day.

            # for event in group_event:
            #     # if self.date not in [i.date for i in events]:
            #     event.date += timedelta(days=(self.date.day - event.date.day))
            #     event.date += timedelta(hours=(self.date.hour - event.date.hour))
            #     event.date += timedelta(minutes=(self.date.minute - event.date.minute))
            #     event.name = self.name
            #     event.cares = self.cares
            #     event.care_address = self.care_address
            #     event.save()
            for date in updated_dates:
                Event.objects.filter(pk=self.id).update(
                    name=self.name,
                    care_address=self.care_address,
                    cares=self.cares,
                    user_id=self.user.id,
                    date=date,
                )

        elif (
            not self.day_per_week
            and self.delta_visit_per_hour
            and self.number_of_days >= 1
        ):
            """Update isolated event inside group."""
            print("upd 3")
            # updates an event that can be single or part of a group of consecutive
            # days without being spaced by a date delta.
            # Several times a day possibly.
            for date in updated_dates:
                Event.objects.filter(pk=self.id).update(
                    name=self.name,
                    care_address=self.care_address,
                    cares=self.cares,
                    user_id=self.user.id,
                    date=date,
                )

        elif (
            self.day_per_week
            and not self.delta_visit_per_hour
            and self.number_of_days > 1
        ):
            for date in updated_dates:
                Event.objects.filter(pk=self.id).update(
                    name=self.name,
                    care_address=self.care_address,
                    cares=self.cares,
                    user_id=self.user.id,
                    date=date,
                )
