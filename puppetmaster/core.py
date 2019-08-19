from django.test import TestCase, Client, modify_settings, override_settings
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver

from .assertions import AssertionsMixin
from .form_filling import FormFillingMixin
from .middleware import AutoLoginMiddleware
from .waiter import WaiterMixin


class BasePuppetMaster:
    DRIVER_WINDOW_WIDTH = 1280
    DRIVER_WINDOW_HEIGHT = 1024

    def __init__(self) -> None:
        self.driver: webdriver.Remote = None

    @property
    def server_url(self) -> str:
        raise NotImplementedError

    @classmethod
    def create_driver(cls) -> webdriver.Remote:
        driver = settings.PM__SELENIUM_DRIVER(
            executable_path=settings.PM__SELENIUM_DRIVER_PATH)
        # XXX: Window size must be explicitly set to avoid issue where elements
        # found in other drivers (e.g. firefox) are not visible in phantomjs.
        # For more details see: https://github.com/ariya/phantomjs/issues/11637
        driver.set_window_size(width=cls.DRIVER_WINDOW_WIDTH,
                               height=cls.DRIVER_WINDOW_HEIGHT)
        return driver


class SeleniumTestsMixin(WaiterMixin,
                         AssertionsMixin,
                         FormFillingMixin):
    """Common class for Selenium tests"""
    should_login_automatically = True
    starting_url = '/'

    def login_automatically(self) -> None:
        raise NotImplementedError

    def setUp(self) -> None:
        self.driver = self.create_driver()
        self.client = Client()

        if self.should_login_automatically:
            self.login_automatically()

        assert len(self.driver.window_handles) > 0, "No window handles!"
        self.initiate_database()
        self.initial_window = self.driver.window_handles[0]
        self.driver.get(self.server_url + self.starting_url)

    def tearDown(self) -> None:
        if isinstance(self.driver, webdriver.Chrome):
            # XXX: fix broken pipe when re-using chrome instance between tests
            # without this code, first test executes and next one hangs
            self.driver.execute_script('location.reload()')
            self.driver.quit()

    def initiate_database(self) -> None:
        # Override and initiate database with data here
        pass

    def switch_to_next_window(self) -> None:
        """Switch Selenium focus to next window (browser tab)"""
        next_window = next(filter(lambda h: h != self.initial_window,
                                  self.driver.window_handles))
        self.driver.switch_to_window(next_window)


class SeleniumTestCase(SeleniumTestsMixin, TestCase):
    @property
    def server_url(self) -> str:
        return settings.PM__SERVICE_URL


@modify_settings(MIDDLEWARE={
    'append': 'puppetmaster.middleware.AutoLoginMiddleware',
    'remove': 'debug_toolbar.middleware.DebugToolbarMiddleware',
})
@override_settings(LOGGERS={
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
    }
})
class SeleniumLiveServerTestCase(SeleniumTestsMixin, StaticLiveServerTestCase):
    @property
    def server_url(self):
        return self.live_server_url

    def create_user(self) -> AbstractUser:
        return get_user_model().objects.create_user(
            username='brucelee',
            password='be_like_water',
            email='example@gmail.com',
            is_staff=False, is_active=True)

    def login_automatically(self) -> None:
        self.user = self.create_user()
        self.verify_email(self.user)
        if self.login_automatically:
            AutoLoginMiddleware.user = self.user
        else:
            AutoLoginMiddleware.user = None
