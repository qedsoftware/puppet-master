from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import InvalidElementStateException

from puppetmaster.form_filling import FormFillingInterface, InputValue


class EnketoFormFillingMixin(FormFillingInterface):
    """
    Wrapper for enketo-specific form filling functions
    """
    # TODO: login to enketo before filling
    DATEPICKER_CLICK_OFFSET = (-300, 0)

    def _fill_date_input(self,
                         virtual_date_input: WebElement,
                         date: InputValue,
                         classname: str) -> None:
        assert type(date) == str
        xpath_selector = f"../div[contains(@class, '{classname}')]/input"
        actual_date_input = virtual_date_input\
            .find_element_by_xpath(xpath_selector)
        try:
            actual_date_input.clear()
        except InvalidElementStateException:
            pass
        actual_date_input.send_keys(date)
        # XXX: After inputting the data a datepicker widget appears, so we need
        # to hide it by clicking on the blank area nearby
        ActionChains(self.driver)\
            .move_to_element(actual_date_input)\
            .move_by_offset(*self.DATEPICKER_CLICK_OFFSET).click().perform()

    def fill_date_input(self, input_el: WebElement, date: InputValue) -> None:
        self._fill_date_input(input_el, date, 'date')

    def fill_time_input(self, input_el: WebElement, time: InputValue) -> None:
        self._fill_date_input(input_el, time, 'timepicker')

    def submit_form(self, form: WebElement) -> None:
        form_selector = ("." + ".".join(form.get_attribute("class").split(" "))
                         if form else 'form')
        submit_button_selector = (
            f'{form_selector} input[type="submit"], '
            '.form-footer__content__main-controls button[id="submit-form"]')
        submit_button = self.wait_for_element(submit_button_selector)
        submit_button.click()
