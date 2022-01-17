"""Test cabinet views module."""
from datetime import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse


from nursapps.cabinet.forms import (
    CreateCabinetForm,
    SearchCabinetForm,
    AssociationValidationForm,
    CancelAssociationForm,
)
from nursapps.cabinet.models import Associate, Cabinet, RequestAssociate

User = get_user_model()
now = datetime.now()


class TestCabinetViews(TestCase):
    """Test Cabinet."""

    def setUp(self):
        """Set Up."""
        self.bill = User.objects.create_user(
            username="bill", email="bill@bool.com", password="poufpouf"
        )

        self.client = Client()

        self.cabinet = Cabinet.objects.create(name="cabbill")
        self.bill.is_cabinet_owner = True
        self.bill.save()
        Associate.objects.create(cabinet_id=self.cabinet.id, user_id=self.bill.id)
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
        # and he wants his own named "cabob"
        self.assertTemplateUsed(response, "registration/create_cabinet.html")
        cabinet_name = "cabob"
        form = CreateCabinetForm(data={"cabinet_name": cabinet_name})
        self.assertTrue(form.is_valid())
        self.assertFalse(Cabinet.objects.filter(name=cabinet_name).exists())

        response = self.client.post(
            url, {"cabinet_name": form.cleaned_data["cabinet_name"]}, follow=True
        )
        self.assertTrue(Cabinet.objects.filter(name=cabinet_name).exists())
        self.bob.is_cabinet_owner = True
        self.bob.save()

        self.assertRedirects(
            response,
            "/auth/accounts/profile/",
            status_code=302,
            target_status_code=200,
        )
        self.assertTemplateUsed(response, "registration/profile.html")

    def test_view_user_create_new_cabinet_redirect_to_ask_for_associate_view(self):
        """Test view user create new cabinet."""
        self.client.force_login(self.bob)
        url = reverse("cabinet:create")
        response = self.client.get(url)
        # After Bob's inscription, he wants to use the app
        self.assertFalse(self.bob.is_cabinet_owner)

        # he wants to join a cabinet already registered
        self.assertTemplateUsed(response, "registration/create_cabinet.html")
        cabinet_name = "cabbill"
        form = CreateCabinetForm(data={"cabinet_name": cabinet_name})
        self.assertTrue(form.is_valid())
        response = self.client.post(url, {"cabinet_name": cabinet_name}, follow=True)
        self.assertTrue(Cabinet.objects.filter(name=cabinet_name).exists())
        self.assertEqual(response.status_code, 200)
        # the cabinet exists and he can send an affiliation request to the owner
        response = self.client.get(reverse("cabinet:askfor"))

        form = SearchCabinetForm(data={"cabinet_name": cabinet_name})
        self.assertTrue(form.is_valid())

        url = reverse("cabinet:askfor")
        response = self.client.post(
            url, {"cabinet_name": form.cleaned_data["cabinet_name"]}, follow=True
        )
        self.assertEqual(response.status_code, 200)

        # The request is send
        self.assertIn(
            "La demande vient d'être envoyée",
            response.content.decode(encoding="utf-8", errors="strict"),
        )
        self.assertTemplateUsed(response, "registration/profile.html")

    def test_confirm_associate(self):
        """Test confirm associate."""
        self.client.force_login(self.bob)
        url = reverse("cabinet:create")
        response = self.client.get(url)
        # After Bob's inscription, he wants to use the app
        self.assertFalse(self.bob.is_cabinet_owner)

        # he wants to join a cabinet already registered
        self.assertTemplateUsed(response, "registration/create_cabinet.html")
        cabinet_name = "cabbill"
        form = CreateCabinetForm(data={"cabinet_name": cabinet_name})
        self.assertTrue(form.is_valid())
        response = self.client.post(url, {"cabinet_name": cabinet_name}, follow=True)
        self.assertTrue(Cabinet.objects.filter(name=cabinet_name).exists())
        self.assertEqual(response.status_code, 200)
        # the cabinet exists and he can send an affiliation request to the owner
        response = self.client.get(reverse("cabinet:askfor"))

        form = SearchCabinetForm(data={"cabinet_name": cabinet_name})
        self.assertTrue(form.is_valid())

        url = reverse("cabinet:askfor")
        response = self.client.post(
            url, {"cabinet_name": form.cleaned_data["cabinet_name"]}, follow=True
        )
        self.assertEqual(response.status_code, 200)

        # The request is send
        self.assertIn(
            "La demande vient d'être envoyée",
            response.content.decode(encoding="utf-8", errors="strict"),
        )
        self.assertTemplateUsed(response, "registration/profile.html")
        self.assertTrue(RequestAssociate.objects.filter(sender_id=self.bob.id).exists())
        association_request = RequestAssociate.objects.filter(receiver_id=self.bill.id)
        association_request = association_request.values_list("sender_id", flat=True)
        sender_request = RequestAssociate.objects.filter(sender_id=self.bob.id)

        self.client.force_login(self.bill)
        # Bill is cabinet owner, in his profile, a request to him is waiting
        profile_url = reverse("nursauth:profile")
        response = self.client.get(profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/profile.html")
        self.assertTrue(self.bill.is_cabinet_owner)

        self.assertNotIn(
            "<td>bob</td><td>bob@bebo.com</td><td> associé  </td>\n",
            response.content.decode(encoding="utf-8", errors="strict"),
        )

        self.assertIn(
            "Vous avez une demande d'association",
            response.content.decode(encoding="utf-8", errors="strict"),
        )

        valid_form = AssociationValidationForm(
            data={"confirm": self.bob.id, "choice": "associate"}
        )
        self.assertTrue(valid_form.is_valid())

        sender_id = valid_form.cleaned_data["confirm"]
        choice = valid_form.cleaned_data["choice"]

        url = "/accounts/profile/confirm-associate/"

        response = self.client.post(
            url,
            {"confirm": sender_id, "choice": choice},
            follow=True,
        )

        self.assertFalse(self.bob.is_cabinet_owner)

        profile_url = reverse("nursauth:profile")
        response = self.client.get(profile_url)

        self.assertIn(
            "<td>bob</td><td>bob@bebo.com</td><td> associé  </td>\n",
            response.content.decode(encoding="utf-8", errors="strict"),
        )

        self.assertTemplateUsed(response, "registration/profile.html")
        self.assertEqual(response.status_code, 200)

    def test_decline_associate(self):
        """Test decline associate."""
        self.client.force_login(self.bob)
        url = reverse("cabinet:create")
        response = self.client.get(url)
        # After Bob's inscription, he wants to use the app
        self.assertFalse(self.bob.is_cabinet_owner)

        # he wants to join a cabinet already registered
        self.assertTemplateUsed(response, "registration/create_cabinet.html")
        cabinet_name = "cabbill"
        form = CreateCabinetForm(data={"cabinet_name": cabinet_name})
        self.assertTrue(form.is_valid())
        response = self.client.post(url, {"cabinet_name": cabinet_name}, follow=True)
        self.assertTrue(Cabinet.objects.filter(name=cabinet_name).exists())
        self.assertEqual(response.status_code, 200)
        # the cabinet exists and he can send an affiliation request to the owner
        response = self.client.get(reverse("cabinet:askfor"))

        form = SearchCabinetForm(data={"cabinet_name": cabinet_name})
        self.assertTrue(form.is_valid())

        url = reverse("cabinet:askfor")
        response = self.client.post(
            url, {"cabinet_name": form.cleaned_data["cabinet_name"]}, follow=True
        )
        self.assertEqual(response.status_code, 200)

        # The request is send
        self.assertIn(
            "La demande vient d'être envoyée",
            response.content.decode(encoding="utf-8", errors="strict"),
        )
        self.assertTemplateUsed(response, "registration/profile.html")
        self.assertTrue(RequestAssociate.objects.filter(sender_id=self.bob.id).exists())
        association_request = RequestAssociate.objects.filter(receiver_id=self.bill.id)
        association_request = association_request.values_list("sender_id", flat=True)
        sender_request = RequestAssociate.objects.filter(sender_id=self.bob.id)

        self.client.force_login(self.bill)
        # Bill is cabinet owner, in his profile, a request to him is waiting
        profile_url = reverse("nursauth:profile")
        response = self.client.get(profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/profile.html")
        self.assertTrue(self.bill.is_cabinet_owner)

        self.assertNotIn(
            "<td>bob</td><td>bob@bebo.com</td><td> associé  </td>\n",
            response.content.decode(encoding="utf-8", errors="strict"),
        )

        self.assertIn(
            "Vous avez une demande d'association",
            response.content.decode(encoding="utf-8", errors="strict"),
        )
        # And now Bill wants to decline the demand
        cancel_form = CancelAssociationForm(data={"cancel": "canceled"})
        self.assertTrue(cancel_form.is_valid())
        url = "/accounts/profile/decline-associate/"
        response = self.client.post(url, {"decline": self.bob.id}, follow=True)

        self.assertFalse(
            RequestAssociate.objects.filter(sender_id=self.bob.id).exists()
        )

        self.assertTemplateUsed(response, "registration/profile.html")
        self.assertEqual(response.status_code, 200)

    def test_cancel_associate_demand(self):
        """Test cancel associate demand."""
        self.client.force_login(self.bob)
        url = reverse("cabinet:create")
        response = self.client.get(url)
        # After Bob's inscription, he wants to use the app
        self.assertFalse(self.bob.is_cabinet_owner)

        # he wants to join a cabinet already registered
        self.assertTemplateUsed(response, "registration/create_cabinet.html")
        cabinet_name = "cabbill"
        form = CreateCabinetForm(data={"cabinet_name": cabinet_name})
        self.assertTrue(form.is_valid())
        response = self.client.post(url, {"cabinet_name": cabinet_name}, follow=True)
        self.assertTrue(Cabinet.objects.filter(name=cabinet_name).exists())
        self.assertEqual(response.status_code, 200)
        # the cabinet exists and he can send an affiliation request to the owner

        self.assertRedirects(
            response,
            "/accounts/profile/ask-for-associate/",
            status_code=302,
            target_status_code=200,
        )

        form = SearchCabinetForm(data={"cabinet_name": cabinet_name})
        self.assertTrue(form.is_valid())

        url = reverse("cabinet:askfor")
        response = self.client.post(
            url, {"cabinet_name": form.cleaned_data["cabinet_name"]}, follow=True
        )
        self.assertEqual(response.status_code, 200)

        # The request is send
        self.assertIn(
            "La demande vient d'être envoyée",
            response.content.decode(encoding="utf-8", errors="strict"),
        )
        self.assertTemplateUsed(response, "registration/profile.html")

        associate = Associate.objects.get(user_id=self.bill.id)
        if associate:
            associates = Associate.objects.get_associates(associate.id)
            cabinet = Cabinet.objects.filter(pk=associate.cabinet_id).first()

        cabinet_associate = Associate.objects.filter(cabinet_id=cabinet.id).first()

        obj, _ = RequestAssociate.objects.get_or_create(
            sender_id=self.bob.id,
            receiver_id=cabinet_associate.user.id,
            cabinet_id=cabinet_associate.cabinet.id,
        )
        self.assertTrue(RequestAssociate.objects.filter(sender_id=self.bob.id).exists())

        # And now Bob wants to cancel his demand
        cancel_form = CancelAssociationForm(data={"cancel": "canceled"})
        self.assertTrue(cancel_form.is_valid())
        url = "/accounts/profile/cancel-associate-demand/"
        response = self.client.post(url, {"cancel": "canceled"}, follow=True)

        self.assertFalse(
            RequestAssociate.objects.filter(sender_id=self.bob.id).exists()
        )

        self.assertRedirects(
            response,
            "/accounts/profile/new-cabinet/",
            status_code=302,
            target_status_code=200,
        )

        self.assertEqual(response.context["current_month"], now.month)
        self.assertEqual(response.context["current_year"], now.year)

        self.assertIn(
            "Création ou affiliation à un cabinet",
            response.content.decode(encoding="utf-8", errors="strict"),
        )

        self.assertTemplateUsed(response, "registration/profile.html")
        self.assertEqual(response.status_code, 200)
