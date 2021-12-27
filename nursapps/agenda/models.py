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
    care_price = models.CharField(max_length=20)
    date = models.DateTimeField(
        null=True,
        blank=True,
    )
    group_id = models.CharField(default=random_group_id, max_length=400)
    total_visit_per_day = models.CharField(max_length=2)
    delta_visit_per_day = models.CharField(max_length=2, default=1)
    delta_visit_per_hour = models.CharField(max_length=2)
    number_of_days = models.CharField(max_length=2)
    day_per_week = models.CharField(max_length=100, null=True)
    # choice_event_edit = models.CharField(max_length=100, null=True)

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

    # @property
    # def random_group_id(self) -> str:
    #     """Generate a random ID to identify a group of event."""
    #     return str(random.randint(1000, 1000000000))

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
                        int(self.delta_visit_per_hour) + ajust
                        if int(self.delta_visit_per_hour) > 3
                        else int(self.delta_visit_per_hour) + ajust + 1
                    )
                    * int(self.total_visit_per_day)
                ),
                int(self.delta_visit_per_hour),
            )
        )

    def by_week_day(self) -> tuple:
        """Return the rrule byweekday parameter."""
        return tuple([int(day_number) for day_number in self.day_per_week.split(", ")])

    def create_weekly_event_with_delta_hour(self, user_id):
        """Create a weekly event with delta in hour."""
        for index in list(range(0, int(self.number_of_days))):
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
                date=[
                    date
                    for date in list(
                        rrule(
                            WEEKLY,
                            count=int(self.number_of_days),
                            wkst=SU,
                            byhour=self.by_hour(),
                            byweekday=self.by_week_day(),
                            dtstart=self.date,
                        )
                    )
                ][index],
            )

    def create_unique_event_per_day_with_week_recurrency(self, user_id):
        """create_unique event per day with week recurrency."""
        for index in list(range(0, int(self.number_of_days))):  # number_of_days
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
                date=[
                    date
                    for date in list(
                        rrule(
                            WEEKLY,
                            count=int(self.number_of_days),
                            wkst=SU,
                            byweekday=self.by_week_day(),
                            dtstart=self.date,
                        )
                    )
                ][index],
            )

    def create_unique_day_at_unique_hour(self, user_id):
        print("Once a day for just one unique day.")
        for i in range(
            0,
            int(self.total_visit_per_day) * int(self.delta_visit_per_day),
            int(self.delta_visit_per_day),
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
        breakpoint()
        dates = self.get_dates()
        for index in range(0, int(self.number_of_days)):
            # In case of unique day at a unique hour during several consecutive days
            print("create 3 bis")
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
        for i in range(
            0,
            int(self.total_visit_per_day) * int(self.delta_visit_per_hour),
            int(self.delta_visit_per_hour),
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

    def create_events(self, user_id):
        """Create events."""
        if self.day_per_week and self.delta_visit_per_hour:
            self.create_weekly_event_with_delta_hour(user_id)

        elif self.day_per_week and not self.delta_visit_per_hour:
            self.create_unique_event_per_day_with_week_recurrency(user_id)
        elif (
            not self.day_per_week
            and not self.delta_visit_per_hour
            and int(self.number_of_days) < 2
        ):
            print("create 3")
            self.create_unique_day_at_unique_hour(user_id)
        elif not self.day_per_week and self.delta_visit_per_day:
            self.create_unique_day_with_recurency_in_days_delta(user_id)

        elif (
            not self.day_per_week
            and not self.delta_visit_per_hour
            and int(self.number_of_days) > 1
        ):
            self.create_unique_day_at_unique_hour_during_several_consecutive_days(
                user_id
            )
        elif not self.day_per_week and self.delta_visit_per_hour:
            print("create 4")
            self.unique_day_with_recurence_in_it(user_id)

    def get_dates(self) -> list:
        """Return a date list."""
        dates = [self.date]
        for index in list(
            range(
                0,
                (
                    int(self.number_of_days) - 1
                    if int(self.number_of_days) >= 3
                    else int(self.number_of_days)
                )
                * int(self.delta_visit_per_day),
                int(self.delta_visit_per_day),
            )
        ):
            self.date += timedelta(days=int(self.delta_visit_per_day))
            dates.append(self.date)
        return dates

    def get_recurency_dates(self) -> list:
        """Return a list of events.

        These are repeated in a day at a frequency in hours between each. With also
        a recurrence of days which can be consecutive or spaced apart by several days.

        For example, twice a day every three days for a total of 5 days.
        """
        dates = []
        for index in range(0, int(self.number_of_days)):
            dates += [
                self.date + timedelta(hours=i)
                for i in range(
                    0,
                    (int(self.total_visit_per_day) * int(self.delta_visit_per_hour)),
                    int(self.delta_visit_per_hour),
                )
                if i + self.date.hour not in [0, 1, 2, 3, 4, 5, 24]
            ]
            self.date += timedelta(days=int(self.delta_visit_per_day))
        return dates

    def update_events(self, group_event, edit_choice):
        """Update events."""
        edit_choice = "".join(edit_choice)

        if edit_choice == "thisone":  # ok
            dates_grp_event = [self.date]
            group_event = [evt for evt in group_event if evt.date == self.date]
        elif edit_choice == "thisone_after":  # ok
            dates_grp_event = [evt.date for evt in group_event if evt.date >= self.date]
            group_event = [event for event in group_event if event.date >= self.date]
        elif edit_choice == "allevent":  # ok
            dates_grp_event = [evt.date for evt in group_event]

        updated_dates = self.updated_date(
            dates_grp_event, self.date.day, self.date.hour, self.date.minute
        )

        if (
            len(self.day_per_week.split(", ")) > 1
            or self.delta_visit_per_hour
            or int(self.number_of_days) > 1
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
            or self.delta_visit_per_hour
            or int(self.number_of_days) > 1
            or len(updated_dates) == 1
        ):
            # Update a unique day and a group of days [with recurency].
            print("upd 1 unique")
            print("unique", group_event)
            for index, event in enumerate(group_event):

                breakpoint()
                if event.date == updated_dates[index]:
                    Event.objects.filter(pk=event.id).update(
                        name=self.name,
                        care_address=self.care_address,
                        cares=self.cares,
                        user_id=self.user.id,
                        date=updated_dates[index],
                    )

        elif (
            not self.day_per_week
            and not self.delta_visit_per_hour
            and int(self.number_of_days) == 1
        ):
            print("upd 2")
            # Update a unique day without recurency
            for event in group_event:
                # if self.date not in [i.date for i in events]:
                event.date += timedelta(days=(self.date.day - event.date.day))
                event.date += timedelta(hours=(self.date.hour - event.date.hour))
                event.date += timedelta(minutes=(self.date.minute - event.date.minute))
                event.name = self.name
                event.cares = self.cares
                event.care_address = self.care_address
                event.save()

        else:
            return True
