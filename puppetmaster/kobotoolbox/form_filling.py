from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import InvalidElementStateException

from puppetmaster.form_filling import FormFillingInterface


# TODO: login to enketo before filling
class EnketoFormFillingMixin(FormFillingInterface):
    """
    Wrapper for enketo-specific form filling functions
    """
    def _fill_date_input(self, virtual_date_input, date, classname):
        assert type(date) == str
        xpath_selector = f"../div[contains(@class, '{classname}')]/input"
        actual_date_input = virtual_date_input\
            .find_element_by_xpath(xpath_selector)
        try:
            actual_date_input.clear()
        except InvalidElementStateException:
            pass
        actual_date_input.send_keys(date)
        ActionChains(self.driver)\
            .move_to_element(actual_date_input)\
            .move_by_offset(-200, 0).click().perform()

    def fill_date_input(self, input, date):
        self._fill_date_input(input, date, 'date')

    def fill_time_input(self, input, time):
        self._fill_date_input(input, time, 'timepicker')

    def submit_form(self, form):
        form_selector = ("." + ".".join(form.get_attribute("class").split(" "))
                         if form else 'form')
        submit_button_selector = (
            f'{form_selector} input[type="submit"], '
            '.form-footer__content__main-controls button[id="submit-form"]')
        submit_button = self.wait_for_element(submit_button_selector)
        submit_button.click()

    def select_option(self, select, **data):
        # Do nothing
        return
