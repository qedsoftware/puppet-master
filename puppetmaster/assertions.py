from selenium.common.exceptions import TimeoutException
from .exceptions import SeleniumAssertionError

from puppetmaster.waiter import WaiterInterface


class AssertionsMixin(WaiterInterface):
    def assert_in_css_selector(self, css_selector: str, message: str) -> None:
        try:
            self.wait(lambda driver: (
                message in
                driver.find_element_by_css_selector(css_selector).text
            ))
        except TimeoutException:
            raise SeleniumAssertionError(f'"{message}" not found in {css_selector}')

    def assert_in_page_source(self, message: str) -> None:
        try:
            self.wait(lambda driver: message in driver.page_source)
        except TimeoutException:
            raise SeleniumAssertionError(f'"{message}" not found in page source.')

    def assert_on_page(self, url_path: str) -> None:
        try:
            self.wait(lambda driver: (
                self.server_url + url_path == driver.current_url
            ))
        except TimeoutException:
            raise SeleniumAssertionError(
                f'Expected page "{url_path}", '
                f'current page: "{self.driver.current_url}".'
            )
