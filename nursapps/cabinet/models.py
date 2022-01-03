"""Cabinet models module."""
from django.db import models
from nursapps.nursauth.models import User
from django.conf import settings


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
