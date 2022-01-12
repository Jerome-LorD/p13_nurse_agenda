"""Cabinet models module."""
from django.db import models
from django.conf import settings

from nursapps.nursauth.models import User


class Cabinet(models.Model):
    """Cabinet assoc model."""

    name = models.CharField(max_length=10, unique=True, default=False, blank=True)

    def __str__(self) -> str:
        """Str representation."""
        return self.name

    class Meta:
        """Meta."""

        ordering = ["name"]


class AssociateManager(models.Manager):
    """Associate manager."""

    def get_associates(self, cabinet):
        """Get associates."""
        associates = self.all().filter(cabinet=cabinet)
        associates = User.objects.filter(pk__in=[asso.user_id for asso in associates])
        return associates

    def is_replacment(self, user):
        """Verify if user is replacment."""
        if not user.is_cabinet_owner:
            return Associate.objects.filter(user_id=user.id).exists()


class Associate(models.Model):
    """Store the user and the cabinet they are affiliated with."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cabinet = models.ForeignKey(Cabinet, on_delete=models.CASCADE)

    objects = AssociateManager()

    def __str__(self) -> str:
        """Str representation."""
        return f"{self.user_id} - {self.cabinet_id}"


class RequestAssociate(models.Model):
    """Request to associate the new user with the owner of the cabinet."""

    sender_id = models.IntegerField(blank=True, null=True)
    receiver_id = models.IntegerField(blank=True, null=True)
    cabinet_id = models.IntegerField(blank=True, null=True)
