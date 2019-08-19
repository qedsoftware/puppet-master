from selenium.common.exceptions import TimeoutException

from puppetmaster.exceptions import SeleniumAssertionError
from puppetmaster.waiter import WaiterInterface


class KobotoolboxAssertionsMixin(WaiterInterface):
    def assert_in_enketo_notification(self, message: str, timeout: int = 1) -> None:
        selector = '#feedback-bar p'
        try:
            self.wait(lambda driver: (
                message in driver.find_element_by_css_selector(selector).text
            ), timeout=timeout)
        except TimeoutException:
            raise SeleniumAssertionError(f'"{message}" not found in notifications.')

    def assert_in_kpi_notifications(self, message: str, timeout: int = 1) -> None:
        selector = '.alertify-notifier .ajs-message'
        try:
            self.wait(lambda driver: any(
                message in elem.text
                for elem in driver.find_elements_by_css_selector(selector)
            ), timeout=timeout)
        except TimeoutException:
            raise SeleniumAssertionError(f'"{message}" not found in notifications.')
