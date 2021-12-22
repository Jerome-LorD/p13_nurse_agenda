"""Selenium test module."""
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.options import Options


class SeleniumTests(StaticLiveServerTestCase):
    """SeleniumTests class."""

    fixtures = ["functional_tests/users.json"]

    @classmethod
    def setUpClass(cls):
        """Set up class."""
        super().setUpClass()
        options = Options()
        options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"

        options.headless = True
        cls.browser = webdriver.Firefox(options=options)
        cls.browser.implicitly_wait(2)
        cls.timeout = 5

    @classmethod
    def tearDownClass(cls):
        """Tear down class."""
        cls.browser.quit()
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

    def test_research_substitutes_as_logged_user(self):
        """Test research substitutes as logged user."""
        self.browser.get("%s%s" % (self.live_server_url, "/auth/accounts/login/"))

        # User Bill wants to log in:
        username_input = self.browser.find_element_by_name("email")
        username_input.send_keys("bill@bool.com")
        password_input = self.browser.find_element_by_name("password")
        password_input.send_keys("poufpouf")
        self.browser.find_element_by_xpath('//button[@value="Log-in"]').click()

        # and now, he wants to log out:
        self.browser.find_element_by_id("Log-out").click()
        self.assertIn("IDE Agenda -- Login", self.browser.title)

    def test_index_title(self):
        """Test Index title is 'Page d'accueil'."""
        self.browser.get(self.live_server_url)
        self.assertIn("IDE Agenda -- Login", self.browser.title)

    def test_agenda_redirect_to_login(self):
        """Test agenda redirect to login with no user connected."""
        self.browser.get(self.live_server_url + "/agenda/2021/12/")
        self.assertIn("IDE Agenda -- Login", self.browser.title)
