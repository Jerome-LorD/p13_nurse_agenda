"""Test cabinet module."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from nursapps.cabinet.models import Associate, Cabinet
from nursapps.cabinet.forms import (
    CreateCabinet,
    SearchForCabinet,
    AssociationValidation,
)

from django.test import Client
from django.urls import reverse
from django.http.response import HttpResponseRedirect

User = get_user_model()


class TestCabinetViews(TestCase):
    """Test Cabinet."""

    def setUp(self):
        """Set Up."""
        self.user = User.objects.create_user(
            username="bill", email="bill@bool.com", password="poufpouf"
        )

        self.client = Client()

        cabinet = Cabinet.objects.create(name="cabbill")
        self.user.is_cabinet_owner = True
        self.user.save()
        Associate.objects.create(cabinet_id=cabinet.id, user_id=self.user.id)
        associate = Associate.objects.filter(user_id=self.user.id).first()

        associates = Associate.objects.get_associates(associate.cabinet_id)
        self.associates = [associate.id for associate in associates]

        self.second_user = User.objects.create_user(
            username="bob", email="bob@bebo.com", password="poufpouf"
        )

    def test_view_create_new_cabinet_uses_correct_template(self):
        """Test view create new cabinet uses correct template."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "nursauth:profile",
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/profile.html")

    def test_view_ask_for_associate_uses_correct_template(self):
        """Test view ask for associate uses correct template."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "cabinet:askfor",
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/askfor.html")

    def test_view_create_new_cabinet_uses_correct_template(self):
        """Test view create new cabinet uses correct template."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "nursauth:profile",
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/profile.html")

    def test_view_confirm_associate_uses_correct_template(self):
        """Test confirm associate uses correct template."""
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "nursauth:profile",
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/profile.html")

    def test_view_user_create_new_cabinet(self):
        self.client.force_login(self.second_user)

        self.assertFalse(self.second_user.is_cabinet_owner)

        # but he has to create a cabinet to do so
        cabinet = Cabinet.objects.create(name="cabob")
        self.second_user.is_cabinet_owner = True
        self.second_user.save()
        self.assertTrue(self.second_user.is_cabinet_owner)

        Associate.objects.create(cabinet_id=cabinet.id, user_id=self.second_user.id)
        associate = Associate.objects.filter(user_id=self.second_user.id).first()

        associates = Associate.objects.get_associates(associate.cabinet_id)
        self.associates = [associate.id for associate in associates]
        response = self.client.get("/agenda/2022/01/10/")
        self.assertEqual(response.status_code, 200)


class TestCreateCabinet(TestCase):
    """Test Create Cabinet form."""

    def setUp(self):
        """Set Up."""

    def test_create_cabinet(self):
        form = CreateCabinet()
        self.assertIn('placeholder="Votre nouveau cabinet"', form.as_ul())

    def test_create_cabinet_redisrect_to_askfor(self):
        form = CreateCabinet(initial={"cabinet": "cabob"})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.initial["cabinet"], "cabob")


class TestSearchForCabinet(TestCase):
    """Test Search For Cabinet form."""

    def setUp(self):
        """Set Up."""

    def test_search_for_cabinet(self):
        form = SearchForCabinet()
        self.assertIn('placeholder="nom du cabinet"', form.as_ul())


class TestAssociationValidation(TestCase):
    """Test Association Validation form."""

    def setUp(self):
        """Set Up."""

    def test_association_validation(self):
        form = AssociationValidation()
        self.assertIn('class="form-control me-2"', form.as_ul())
