"""Test cabinet module."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.shortcuts import redirect

from nursapps.cabinet.forms import (
    CreateCabinetForm,
    SearchCabinetForm,
    AssociationValidationForm,
)
from nursapps.cabinet.models import Associate, Cabinet, RequestAssociate

User = get_user_model()


class TestCabinetViews(TestCase):
    """Test Cabinet."""

    def setUp(self):
        """Set Up."""
        self.bill = User.objects.create_user(
            username="bill", email="bill@bool.com", password="poufpouf"
        )

        self.client = Client()

        cabinet = Cabinet.objects.create(name="cabbill")
        self.bill.is_cabinet_owner = True
        self.bill.save()
        Associate.objects.create(cabinet_id=cabinet.id, user_id=self.bill.id)
        associate = Associate.objects.filter(user_id=self.bill.id).first()

        associates = Associate.objects.get_associates(associate.cabinet_id)
        self.associates = [associate.id for associate in associates]

        self.bob = User.objects.create_user(
            username="bob", email="bob@bebo.com", password="poufpouf"
        )

    def test_view_create_new_cabinet_uses_correct_template(self):
        """Test view create new cabinet uses correct template."""
        self.client.force_login(self.bill)
        profile_url = reverse("nursauth:profile")
        response = self.client.get(profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/profile.html")

    def test_view_ask_for_associate_uses_correct_template(self):
        """Test view ask for associate ."""
        self.client.force_login(self.bill)
        askfor_url = reverse("cabinet:askfor")
        response = self.client.get(askfor_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/askfor.html")

    def test_view_create_new_cabinet_uses_correct_template(self):
        """Test view create new cabinet uses correct template."""
        self.client.force_login(self.bill)
        profile_url = reverse("nursauth:profile")
        response = self.client.get(profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/profile.html")

    def test_view_confirm_associate_uses_correct_template(self):
        """Test confirm associate uses correct template."""
        self.client.force_login(self.bill)
        profile_url = reverse("nursauth:profile")
        response = self.client.get(profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/profile.html")

    def test_view_user_create_new_cabinet(self):
        """Test view user create new cabinet."""
        self.client.force_login(self.bob)
        url = reverse("cabinet:create")
        response = self.client.get(url)
        # After Bob's inscription, he wants to use the app
        self.assertFalse(self.bob.is_cabinet_owner)

        # but he has to create a cabinet to do so
        # and he wants his own
        self.assertTemplateUsed(response, "registration/create_cabinet.html")
        cabinet_name = "cabob"
        form = CreateCabinetForm(data={"cabinet_name": cabinet_name})
        self.assertTrue(form.is_valid())
        self.assertFalse(Cabinet.objects.filter(name=cabinet_name).exists())
        Cabinet.objects.create(name="cabob")
        self.bob.is_cabinet_owner = True
        self.bob.save()
        self.assertTemplateUsed(response, "registration/profile.html")

    def test_view_ask_for_associate_user_can_use_datas_on_shared_planning(self):
        """Test if user can use datas on shared planning.

        A new user who wants to see the data of a cabinet that is not his own must ask
        its owner to become an associate (or replacement).
        """
        self.client.force_login(self.bob)
        self.assertFalse(self.bob.is_cabinet_owner)

        # he wants to see and use the datas on bill's cabinet
        cabinet = "cabbill"
        # Bob search for "cabill" cabinet
        form = SearchCabinetForm(data={"cabinet_name": cabinet})
        self.assertTrue(form.is_valid())
        cabinet = Cabinet.objects.filter(name=form.data["cabinet_name"])
        cabinet = cabinet.first()
        # the cabinet exists
        self.assertIsNotNone(cabinet)
        # He has to make a affiliation demand
        askfor_url = reverse("cabinet:askfor")
        response = self.client.get(askfor_url)
        self.assertEqual(response.status_code, 200)

        cabinet_associate = Associate.objects.filter(cabinet_id=cabinet.id).first()
        obj, _ = RequestAssociate.objects.get_or_create(
            sender_id=self.bob.id,
            receiver_id=cabinet_associate.user_id,
            cabinet_id=cabinet_associate.cabinet_id,
        )

        self.assertEqual(obj.receiver_id, self.bill.id)
        self.assertEqual(obj.sender_id, self.bob.id)

        # Bill has to accept and choice bitween associate or replacment
        # he choose associate and then valid
        self.client.force_login(self.bill)
        self.assertTrue(self.bill.is_cabinet_owner)
        valid_form = AssociationValidationForm(
            data={"confirm": self.bob.id, "choice": "associate"}
        )
        # breakpoint()
        self.assertTrue(valid_form.is_valid())

        # Associate.objects.create(cabinet_id=cabinet.id, user_id=self.bob.id)


class TestCreateCabinetForm(TestCase):
    """Test Create Cabinet form."""

    def setUp(self):
        """Set Up."""
        self.bill = User.objects.create_user(
            username="bill", email="bill@bool.com", password="poufpouf"
        )

        self.client = Client()
        associate = Associate.objects.filter(user_id=self.bill.id)
        associate = associate.first()
        if associate:
            associate.get_associates(associate.id)
            cabinet_id = associate.cabinet_id
            # breakpoint()
            self.cabinet = Cabinet.objects.filter(pk=cabinet_id).first()
        self.bob = User.objects.create_user(
            username="bob", email="bob@bebo.com", password="poufpouf"
        )

    def test_create_cabinet_placeholder(self):
        """Test create cabinet placeholder."""
        form = CreateCabinetForm()
        self.assertIn('placeholder="Votre nouveau cabinet"', form.as_ul())

    def test_create_cabinet_form_returns_expected_value(self):
        """Test create cabinet form returns expected value."""
        self.client.force_login(self.bob)
        form = CreateCabinetForm(data={"cabinet_name": "cabob"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.data["cabinet_name"], "cabob")

    def test_create_cabinet_is_not_already_registered(self):
        """Test create cabinet is not already registered."""
        cabinet = "cabill"
        # response = self.client.post(
        #     "/auth/accounts/profile/", data={"cabinet": "cabob"}
        # )

        form = CreateCabinetForm(data={"cabinet_name": "cabill"})
        self.assertTrue(form.is_valid())
        # breakpoint()
        cabinet = Cabinet.objects.create(name="cabill")
        self.assertEqual(cabinet.name, "cabill")


class TestSearchCabinetForm(TestCase):
    """Test Search For Cabinet form."""

    def setUp(self):
        """Set Up."""
        self.bill = User.objects.create_user(
            username="bill", email="bill@bool.com", password="poufpouf"
        )

        self.bob = User.objects.create_user(
            username="bob", email="bob@bool.com", password="poufpouf"
        )

        self.client = Client()

        cabinet = Cabinet.objects.create(name="cabill")
        self.bill.is_cabinet_owner = True
        self.bill.save()
        associate = Associate.objects.create(
            cabinet_id=cabinet.id, user_id=self.bill.id
        )

        associate = Associate.objects.filter(user_id=self.bill.id)
        associate = associate.first()
        if associate:
            Associate.objects.get_associates(associate.id)
            cabinet_id = associate.cabinet_id
            self.cabinet = Cabinet.objects.filter(pk=cabinet_id).first()

    def test_cabinet_name_placeholder(self):
        """Test search for cabinet placeholder."""
        form = SearchCabinetForm()
        self.assertIn('placeholder="nom du cabinet"', form.as_ul())

    def test_cabinet_name_from_new_user(self):
        """Test search for cabinet from new user."""
        cabinet = "cabill"
        # Bob search for "cabill" cabinet
        form = SearchCabinetForm(data={"cabinet_name": cabinet})
        self.assertTrue(form.is_valid())
        cabinet = Cabinet.objects.filter(name=form.data["cabinet_name"])
        cabinet = cabinet.first()
        # the cabinet exists
        self.assertIsNotNone(cabinet)
        # He has to make a affiliation demand
        askfor_url = reverse("cabinet:askfor")
        response = self.client.get(askfor_url)
        self.assertEqual(response.status_code, 302)

        cabinet_associate = Associate.objects.filter(cabinet_id=cabinet.id).first()
        obj, _ = RequestAssociate.objects.get_or_create(
            sender_id=self.bob.id,
            receiver_id=cabinet_associate.user_id,
            cabinet_id=cabinet_associate.cabinet_id,
        )

        self.assertEqual(obj.receiver_id, self.bill.id)
        self.assertEqual(obj.sender_id, self.bob.id)


class TestAssociationValidationForm(TestCase):
    """Test Association Validation form."""

    def setUp(self):
        """Set Up."""

    def test_association_validation_form_class_contains_expected_values(self):
        """Test_association_validtation_class_contains_expected_values."""
        form = AssociationValidationForm()
        self.assertIn('class="form-control me-2"', form.as_ul())


class TestAutoComplete(TestCase):
    """Test autocomplete."""

    def setUp(self):
        """Set Up."""
        self.bill = User.objects.create_user(
            username="bill", email="bill@bool.com", password="poufpouf"
        )

        self.client = Client()

    def test_autocomplete_returns_status_code_200_and_expected_content_type(self):
        """Test autocomplete returns status_code 200 and expected content type."""
        response = self.client.get("/autocomplete/?q=cabob")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
