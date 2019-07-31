from django.test import TestCase, Client, modify_settings, override_settings
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model, login

from selenium import webdriver

from .assertions import AssertionsMixin
from .form_filling import FormFillingMixin
from .waiter import WaiterMixin


def create_driver() -> webdriver.Remote:
    driver = settings.SELENIUM_DRIVER(
        executable_path=settings.SELENIUM_DRIVER_PATH)
    # window size must be explicitly set to avoid issue where elements
    # found in other drivers (e.g. firefox) are not visible in phantomjs.
    # For more details see: https://github.com/ariya/phantomjs/issues/11637
    driver.set_window_size(width=1280, height=1024)
    return driver


class AutoLoginMiddleware:
    user = None

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self.user is not None:
            login(request, self.user)
        return self.get_response(request)


@modify_settings(MIDDLEWARE={
    'append': 'selenium_tests.common.AutoLoginMiddleware',
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
# TODO: split live server and tests case
class SeleniumTestCase(TestCase,
                       WaiterMixin,
                       AssertionsMixin,
                       FormFillingMixin):
    """Common class for Selenium tests"""
    login_automatically = True
    starting_url = '/'
    USERNAME = settings.USERNAME  # TODO
    PASSWORD = settings.PASSWORD

    def setUp(self) -> None:
        self.driver = create_driver()
        self.client = Client()

        # TODO
        # if self.login_automatically:
        #     self.log_in_as_user(self.USERNAME, self.PASSWORD)

        # self.user = self.create_user()
        # self.verify_email(self.user)
        # if self.login_automatically:
        #     AutoLoginMiddleware.user = self.user
        # else:
        #     AutoLoginMiddleware.user = None

        assert len(self.driver.window_handles) > 0, "No window handles!"
        self.initiate_database()
        self.initial_window = self.driver.window_handles[0]
        # self.driver.get(settings.KPI_ADDR + self.starting_url)  # TODO
        # TODO: live_server_url
        self.driver.get(self.live_server_url + self.starting_url)

    def tearDown(self) -> None:
        if isinstance(self.driver, webdriver.Chrome):
            # XXX: fix broken pipe when re-using chrome instance between tests
            # without this code, first test executes and next one hangs
            self.driver.execute_script('location.reload()')
            self.driver.quit()

    def initiate_database(self) -> None:
        # Override and initiate database with data here
        pass

    def create_user(self) -> AbstractUser:
        return get_user_model().objects.create_user(
            username='brucelee',
            password='be_like_water',
            email='example@gmail.com',
            is_staff=False, is_active=True)

    def switch_to_next_window(self) -> None:
        """Switch Selenium focus to next window (browser tab)"""
        next_window = next(filter(lambda h: h != self.initial_window,
                                  self.driver.window_handles))
        self.driver.switch_to_window(next_window)
