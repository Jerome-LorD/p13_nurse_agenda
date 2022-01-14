"""Tests nursauth module."""
from django.contrib.auth import get_user_model
from django.test import TestCase, Client


class TestUserRegistration(TestCase):
    """Test user registration."""

    def setUp(self):
        """Set up."""
        User = get_user_model()
        self.bill = User
        self.inscript_credentials = {
            "email": "john@doe.com",
            "username": "john",
            "password1": "poufpouf",
            "password2": "poufpouf",
        }

        self.bill = User.objects.create_user(
            username="bill", email="bill@bool.com", password="poufpouf"
        )

        self.client = Client()

    def test_user_registration(self):
        """Test form data.

        The view needs at least:
        - email
        - username
        - password 1 & 2

        If the registration is complete, the page is redirected to the profile page if
        the user has a cabinet otherwise it redirects to the new-cabinet page.

        Expected redirect: "/accounts/profile/new-cabinet/"
        """
        response = self.client.post(
            "/auth/accounts/inscript/", self.inscript_credentials
        )
        self.assertEqual(response.status_code, 302)
        response = self.client.get("/auth/accounts/profile/")
        self.assertRedirects(
            response,
            "/accounts/profile/new-cabinet/",
            status_code=302,
            target_status_code=200,
        )

    def test_user_login(self):
        """Test user login.

        If the login succeed, it is also redirected to the profile page if the user
        has a cabinet otherwise it redirects to the new-cabinet page.

        Expected redirect: "/accounts/profile/new-cabinet/"
        """
        response = self.client.get("/auth/accounts/login/")
        self.client.force_login(self.bill)
        self.assertTrue(self.bill.is_authenticated)
        response = self.client.get("/auth/accounts/profile/")
        self.assertRedirects(
            response,
            "/accounts/profile/new-cabinet/",
            status_code=302,
            target_status_code=200,
        )
