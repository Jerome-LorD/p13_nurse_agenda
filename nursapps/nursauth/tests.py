"""Tests nursauth module."""
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

# from nursapps.nursauth.forms import NewLoginForm


class TestUserRegistration(TestCase):
    """Test user registration."""

    def setUp(self):
        """SetUp."""
        self.User = get_user_model()
        self.client = Client()
        self.inscript_credentials = {
            "email": "john@doe.com",
            "username": "john",
            "password1": "poufpouf",
            "password2": "poufpouf",
        }
        self.login_credentials = {"email": "john@doe.com", "password": "poufpouf"}

    def test_user_registration(self):
        """test form data.

        The view needs at least:
        - an email
        - a username
        - a password 1 & 2

        If the registration is complete, the page is redirected
        """
        response = self.client.post(
            "/auth/accounts/inscript/", self.inscript_credentials
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(self.User.objects.all()), 1)
