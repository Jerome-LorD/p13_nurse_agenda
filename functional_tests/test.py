"""Selenium test module."""
import os

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


class SeleniumTests(StaticLiveServerTestCase):
    """SeleniumTests class."""

    fixtures = ["functional_tests/users.json"]

    @classmethod
    def setUpClass(cls):
        """Set up class."""
        super().setUpClass()
        options = Options()
        options.add_argument("-headless")
        service = Service(
            executable_path=r"F:\DjangoProjets\p13_nurse_agenda\functional_tests\geckodriver.exe"
        )
        if os.name == "nt":
            options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
            cls.browser = webdriver.Firefox(service=service, options=options)

        cls.browser = webdriver.Firefox(options=options)
        cls.browser.implicitly_wait(2)
        cls.timeout = 5

    @classmethod
    def tearDownClass(cls):
        """Tear down class."""
        cls.browser.quit()
        if os.name == "nt":
            os.system("taskkill /f /im firefox.exe /T")
        super().tearDownClass()

    def test_login_redirect_to_profile(self):
        """Test user login and page redirect to profile."""
        self.browser.get("%s%s" % (self.live_server_url, "/auth/accounts/login/"))

        # User Bill want to log in and consult is profile:
        username_input = self.browser.find_element_by_name("email")
        username_input.send_keys("bill@bool.com")
        password_input = self.browser.find_element_by_name("password")
        password_input.send_keys("poufpouf")
        self.browser.find_element_by_xpath('//button[@value="Log-in"]').click()
        self.assertIn("IDE Agenda -- Mon compte", self.browser.title)

    def test_login_and_logout(self):
        """Test login and then logout."""
        self.browser.get("%s%s" % (self.live_server_url, "/auth/accounts/login/"))

        # User Bill wants to log in:
        username_input = self.browser.find_element_by_name("email")
        username_input.send_keys("bill@bool.com")
        password_input = self.browser.find_element_by_name("password")
        password_input.send_keys("poufpouf")
        self.browser.find_element_by_xpath('//button[@value="Log-in"]').click()
        self.assertIn("IDE Agenda -- Mon compte", self.browser.title)

        # and now, he wants to log out:
        self.browser.find_element_by_id("drop-down").click()
        self.browser.implicitly_wait(2)
        self.browser.find_element_by_id("Log-out").click()
        self.browser.implicitly_wait(2)
        self.browser.find_element_by_id("Logout").click()
        self.assertIn("IDE Agenda -- Accueil", self.browser.title)

    def test_index_title(self):
        """Test Index title is 'Page d'accueil'."""
        self.browser.get(self.live_server_url)
        self.assertIn("IDE Agenda -- Accueil", self.browser.title)

    def test_agenda_redirect_to_login(self):
        """Test agenda redirect to login with no user connected."""
        self.browser.get(self.live_server_url + "/agenda/2021/12/")
        self.assertIn("IDE Agenda -- Login", self.browser.title)

    def test_login_create_event_and_logout(self):
        """Test login create event and logout."""
        self.browser.get("%s%s" % (self.live_server_url, "/auth/accounts/login/"))

        # User Bill wants to log in:
        username_input = self.browser.find_element_by_name("email")
        username_input.send_keys("bill@bool.com")
        password_input = self.browser.find_element_by_name("password")
        password_input.send_keys("poufpouf")
        self.browser.find_element_by_xpath('//button[@value="Log-in"]').click()
        self.assertIn("IDE Agenda -- Mon compte", self.browser.title)

        # to create a single event for the next day at 08:00
        # so he has to go to the main agenda ans then click on the wanted date
        self.browser.find_element_by_id("planning").click()
        self.assertIn("IDE Agenda -- Planning de January", self.browser.title)

        # and now, he wants to log out:
        self.browser.find_element_by_id("drop-down").click()
        self.browser.implicitly_wait(2)
        self.browser.find_element_by_id("Log-out").click()
        self.browser.implicitly_wait(2)
        self.browser.find_element_by_id("Logout").click()
        self.assertIn("IDE Agenda -- Accueil", self.browser.title)
