"""Agenda models module."""
import random

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from nursapps.nursauth.models import User
from django.urls import reverse
from dateutil.rrule import WEEKLY, rrule, SU, MO, TU, WE, TH, FR, SA
from dateutil.parser import *

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
    days_number = models.CharField(max_length=2)
    day_per_week = models.CharField(max_length=100, null=True)

    objects = EventManager()

    def __str__(self) -> str:
        """Return str representation."""
        return f"{self.user} - {self.group_id} - {self.name} - {self.care_address} - {self.cares} - {self.care_price} - {self.date} - {self.day_per_week}"

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

    def create_events(self, user_id):
        """Create events."""
        # If some days are selected for recurrency
        # if not self.delta_visit_per_hour:
        #     self.delta_visit_per_hour = 1
        if self.day_per_week and self.delta_visit_per_hour:
            breakpoint()
            for index in list(range(0, int(self.days_number))):  # number_of_days
                Event.objects.create(
                    total_visit_per_day=self.total_visit_per_day,
                    delta_visit_per_day=self.delta_visit_per_day,
                    delta_visit_per_hour=self.delta_visit_per_hour,
                    days_number=self.days_number,
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
                                count=int(self.days_number),
                                wkst=SU,
                                byhour=tuple(
                                    range(
                                        int(self.date.hour),
                                        (
                                            int(self.date.hour)
                                            * int(self.total_visit_per_day)
                                        ),
                                        int(self.delta_visit_per_hour),
                                    )
                                ),
                                byweekday=tuple(
                                    [
                                        int(day_number)
                                        for day_number in self.day_per_week.split(", ")
                                    ]
                                ),
                                dtstart=self.date,
                            )
                        )
                    ][index],
                )

        # Unique event per day with week recurrency
        elif self.day_per_week and not self.delta_visit_per_hour:

            for index in list(range(0, int(self.days_number))):  # number_of_days
                Event.objects.create(
                    total_visit_per_day=self.total_visit_per_day,
                    delta_visit_per_day=self.delta_visit_per_day,
                    days_number=self.days_number,
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
                                count=int(self.days_number),
                                wkst=SU,
                                byweekday=tuple(
                                    [
                                        int(day_number)
                                        for day_number in self.day_per_week.split(", ")
                                    ]
                                ),
                                dtstart=self.date,
                            )
                        )
                    ][index],
                )
