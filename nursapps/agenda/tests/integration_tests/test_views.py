"""Test agenda views module."""
from dateutil.parser import *
from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from nursapps.agenda.models import Event, Events
from nursapps.agenda.forms import EditEventForm
from nursapps.cabinet.models import Associate, Cabinet


User = get_user_model()

now = datetime.now()


class TestAgendaViews(TestCase):
    """Test Agenda views."""

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

        self.events = Events.objects.create()

        total_visit_per_day = 1
        delta_visit_per_day = 1
        delta_visit_per_hour = 0
        number_of_days = 1
        name = "Client n1"
        care_address = "1 rue du chemin"
        cares = "AB, CD, EF"
        events_id = self.events.id
        date = datetime(2021, 12, 31, 6, 0)

        for i in range(
            0,
            total_visit_per_day * delta_visit_per_day,
            delta_visit_per_day,
        ):
            self.event = Event.objects.create(
                total_visit_per_day=total_visit_per_day,
                delta_visit_per_day=delta_visit_per_day,
                delta_visit_per_hour=delta_visit_per_hour,
                number_of_days=number_of_days,
                name=name,
                care_address=care_address,
                cares=cares,
                user_id=self.bill.id,
                events_id=events_id,
                date=date + timedelta(days=i),
            )

        hour = date.strftime("%H:%M")
        self.hour_, self.minute_ = (int(i) for i in hour.split(":"))

        self.bob = User.objects.create_user(
            username="bob", email="bob@bebo.com", password="poufpouf"
        )

    def test_view_agenda_uses_correct_template(self):
        """Test view agenda uses correct template."""
        self.client.force_login(self.bill)

        now = datetime.now()
        response = self.client.get(
            reverse(
                "nurse:main_agenda",
                args=[str(now.year), str(now.month)],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/agenda.html")

    def test_view_create_event_uses_correct_template(self):
        """Test view create event uses correct template."""
        self.client.force_login(self.bill)

        now = datetime.now()
        hour = "06:00"
        response = self.client.get(
            reverse(
                "nurse:new_event",
                kwargs={
                    "year": now.year,
                    "month": now.month,
                    "day": now.day,
                    "hour": hour,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/event.html")

    def test_view_edit_event_uses_correct_template(self):
        """Test view edit event uses correct template."""
        self.client.force_login(self.bill)

        now = datetime.now()
        hour = "06:00"
        event_id = self.event.id
        response = self.client.get(
            reverse(
                "nurse:edit_event",
                args=[str(now.year), str(now.month), str(now.day), hour, event_id],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/event.html")
        self.assertEqual(response.status_code, 200)

    def test_view_delete_event(self):
        """Test view delete event."""
        self.client.force_login(self.bill)
        event_id = self.event.id
        response = self.client.get(
            reverse(
                "nurse:del_event",
                args=["2021", "12", "31", "06:00", event_id],
            )
        )

        hour_, minute_ = (int(i) for i in "06:00".split(":"))
        event = Event.objects.filter(pk=event_id).first()

        url = f"/agenda/2021/12/31/rdv/06:00/edit/{event_id}/del_event/"

        response = self.client.post(url, {"value": "Oui"}, follow=True)

        group_event = Event.objects.filter(events_id=event.events_id)
        event.delete_event(group_event, "2021", "12", "31", hour_, minute_)
        self.assertFalse(Event.objects.filter(events_id=event.events_id).exists())
        self.assertRedirects(
            response,
            reverse(
                "nurse:daily_agenda",
                kwargs={"year": "2021", "month": "12", "day": "31"},
            ),
        )
        self.assertEqual(response.status_code, 200)

    def test_view_daily_agenda_uses_correct_template(self):
        """Test view daily agenda uses correct template."""
        self.client.force_login(self.bill)

        now = datetime.now()
        response = self.client.get(
            reverse(
                "nurse:daily_agenda",
                args=[str(now.year), str(now.month), str(now.day)],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/daily_agenda_details.html")

    def test_view_redirect_to_create_new_cabinet_if_user_not_cabinet_owner(self):
        """Test view redirect to create new cabinet if user not cabinet owner."""
        self.client.force_login(self.bob)
        self.assertFalse(self.bob.is_cabinet_owner)

        # Bob tries to use the app
        response = self.client.get("/agenda/2022/01/10/")
        # and the targeted link redirect to profile
        self.assertRedirects(
            response,
            "/auth/accounts/profile/",
            status_code=302,
            target_status_code=302,
        )
        response = self.client.get("/auth/accounts/profile/")
        # and profile redirects to new_cabinet
        self.assertRedirects(
            response,
            "/accounts/profile/new-cabinet/",
            status_code=302,
            target_status_code=200,
        )

    def test_wrong_url_leads_to_404_status_code(self):
        """Test wrong url leads to 404 html page."""
        response = self.client.get("/agenda/2022/01/10/rdv/08:00/edit/262/blabla")
        self.assertEqual(response.status_code, 404)

    def test_url_leads_to_302_status_code(self):
        """Test url leads to 302 status code."""
        response = self.client.get("/agenda/2022/01/10/")
        self.assertEqual(response.status_code, 302)

    def test_url_leads_to_200_status_code(self):
        """Test url leads to 200 status code."""
        self.client.force_login(self.bill)
        response = self.client.get("/agenda/2022/1/3/")
        self.assertEqual(response.status_code, 200)

    def test_view_redirects_to_valid_url_if_day_number_gt_maximum_day_number(self):
        """Test view redirects to valid url if day number greater than max day number.

        The valid url is /agenda/current_year/current_month/current_day/
        """
        self.client.force_login(self.bill)
        response = self.client.get(f"/agenda/2022/1/32/")

        self.assertRedirects(
            response,
            f"/agenda/{now.year}/{now.month}/{now.day}/",
            status_code=302,
            target_status_code=200,
        )

    def test_view_redirects_to_valid_url_if_day_number_number_lt_1(self):
        """Test view uses correct template if day number less than 1.

        The valid url is /agenda/current_year/current_month/current_day/
        """
        self.client.force_login(self.bill)
        response = self.client.get(f"/agenda/2022/1/0/")

        self.assertRedirects(
            response,
            f"/agenda/{now.year}/{now.month}/{now.day}/",
            status_code=302,
            target_status_code=200,
        )

    def test_view_redirects_to_valid_url_if_month_number_gt_12(self):
        """Test view redirects to valid url if month number is greater than 12.

        The valid url is /agenda/current_year/current_month/
        """
        self.client.force_login(self.bill)
        response = self.client.get(f"/agenda/2022/13/")

        self.assertRedirects(
            response,
            f"/agenda/{now.year}/{now.month}/",
            status_code=302,
            target_status_code=200,
        )

    def test_view_redirects_to_valid_url_if_month_number_lt_1(self):
        """Test view redirects to valid url if month number less than 1.

        The valid url is /agenda/current_year/current_month/
        """
        self.client.force_login(self.bill)
        response = self.client.get(f"/agenda/2022/0/")

        self.assertRedirects(
            response,
            f"/agenda/{now.year}/{now.month}/",
            status_code=302,
            target_status_code=200,
        )

    def test_view_error_404(self):
        """Test view error_404 return expected status code."""
        response = self.client.get("/agenda/blablablibli/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "pages/404.html")
