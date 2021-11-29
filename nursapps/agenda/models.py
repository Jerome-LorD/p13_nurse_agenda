"""Agenda models module."""

from django.db import models

# from django.urls import reverse

from django.conf import settings

# from django.utils import timezone
from django.contrib.auth import get_user_model

# from django.utils.translation import ugettext_lazy as _

from nursapps.nursauth.models import User

UserModel = get_user_model()


class Cabinet(models.Model):
    """Cabinet assoc model."""

    name = models.CharField(max_length=240, unique=True, default=False, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class AssociateManager(models.Manager):
    """Associate manager."""

    def get_associates(self, cabinet_id):
        """Get associates."""
        associate = self.all().filter(cabinet_id=cabinet_id)
        associates = User.objects.filter(id__in=[item.user_id for item in associate])
        return associates


class Associate(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cabinet = models.ForeignKey(Cabinet, on_delete=models.CASCADE)

    objects = AssociateManager()

    def __str__(self) -> str:
        """Str representation."""
        return f"{self.user} - {self.cabinet}"


class RequestAssociate(models.Model):
    sender_id = models.CharField(max_length=10, default=False, blank=True)
    receiver_id = models.CharField(max_length=10, default=False, blank=True)
    cabinet_id = models.CharField(max_length=10, default=False, blank=True)


class Patient(models.Model):
    cabinet = models.ForeignKey(Cabinet, on_delete=models.CASCADE)
    sex = models.CharField(max_length=1, default=False, blank=True)
    firstname = models.CharField(max_length=240, default=False, blank=True)
    lastname = models.CharField(max_length=240, default=False, blank=True)
    address = models.CharField(max_length=240, default=False, blank=True)
    phone_number = models.CharField(max_length=10, default=False, blank=True)
    typeofcare = models.CharField(max_length=100, default=False, blank=True)
    numberofcare = models.CharField(max_length=2, default=False, blank=True)
    frequency = models.CharField(max_length=2, default=False, blank=True)
    days = models.CharField(max_length=2, default=False, blank=True)
