"""Authenticate module."""
from django.contrib.auth import get_user_model


UserModel = get_user_model()


class EmailAuth:
    """Email authentication class."""

    def authenticate(self, request, email=None, password=None, **kwargs):
        """authenticate."""
        if email is None:
            email = kwargs.get(UserModel.EMAIL_FIELD)
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def user_can_authenticate(self, user):
        """User can authenticate."""
        is_active = getattr(user, "is_active", None)
        return is_active or is_active is None

    def get_user(self, user_id):
        """Get user."""
        try:
            user = UserModel._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None
