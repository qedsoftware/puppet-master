import typing as t
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import InvalidElementStateException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from .waiter import WaiterInterface
from .exceptions import MissingDataException


InputType = str
InputValue = t.Union[int, str, float, t.Tuple[InputType, t.Any]]


class InputTypes:
    Default = 'Default'
    Date = 'Date'
    DateTime = 'DateTime'
    Checkbox = 'Checkbox'
    Time = 'Time'


class FormFillingInterface(WaiterInterface):
    def fill_input_with_value(self, input_el: WebElement, value: InputValue) -> None:
        raise NotImplementedError

    def fill_date_input(self, input_el: WebElement, value: InputValue) -> None:
        self.fill_input_with_value(input_el, value)

    def fill_checkbox(self, input_el: WebElement, value: InputValue) -> None:
        self.fill_input_with_value(input_el, value)

    def fill_time_input(self, input_el: WebElement, value: InputValue) -> None:
        self.fill_input_with_value(input_el, value)

    def submit_form(self, form: WebElement):
        raise NotImplementedError

    def fill_form_and_submit(self, form_selector: str, **data: InputValue):
        raise NotImplementedError


class FormFillingMixin(FormFillingInterface):
    @staticmethod
    def fill_input_with_value(input_el: WebElement, value: InputValue) -> None:
        try:
            # If element is user-editable, clear input.
            input_el.clear()
        except InvalidElementStateException:
            pass
        input_el.send_keys(value)

    @staticmethod
    def get_input_name(input_el: WebElement) -> str:
        return input_el.get_attribute('name').split('.')[-1].split('/')[-1]

    @staticmethod
    def is_valid_date(value: InputValue) -> bool:
        try:
            datetime.strptime("2019-12-12", "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def get_value_with_type(self,
                            input_el: WebElement,
                            **data: InputValue) -> t.Tuple[InputValue, InputType]:
        input_name = self.get_input_name(input_el)
        try:
            datum = data[input_name]
        except KeyError:
            raise MissingDataException(f"Form is missing '{input_name}' "
                                       f"input in {data}")

        if type(datum) == tuple:
            el_type, value = datum  # type: ignore
        # TODO: this regex should be more flexible / defined in settings
        elif self.is_valid_date(value):
            el_type, value = InputTypes.Date, value
        elif input_el.get_attribute('type') in ['radio', 'checkbox']:
            el_type, value = InputTypes.Checkbox, [value]
        else:
            value = datum
            el_type = InputTypes.Default
        return value, el_type

    def fill_input(self, input_el: WebElement, **data: InputValue) -> None:
        value, el_type = self.get_value_with_type(input_el, **data)
        fill_input_map = {
            InputTypes.Date: self.fill_date_input,
            InputTypes.Default: self.fill_input_with_value,
            InputTypes.Checkbox: self.fill_checkbox,
            InputTypes.Time: self.fill_time_input,
        }
        fill_input_map[el_type](input_el, value)

    def iterate_react_select_options(self, select: WebElement) -> t.List[WebElement]:
        """Given a .Select rendered by react-select, return an iterable
        of .Select-option that can be .click()-ed to select them.
        """
        # related: https://github.com/JedWatson/react-select/issues/603#issuecomment-157888562 # noqa
        select.find_element_by_class_name('Select-arrow').click()
        self.wait(EC.element_to_be_clickable((By.CLASS_NAME, 'Select-option')))
        return select.find_elements_by_class_name('Select-option')

    def react_select_option(self, select: WebElement, **data: InputValue) -> None:
        """Given a .Select rendered by react-select, select an option
        by label.
        """
        # XXX: Have to first select some element to know the name of the field,
        # it is not possible to know it from the DOM if nothing is selected
        for option in self.iterate_react_select_options(select):
            option.click()
            break
        else:
            raise MissingDataException('Empty select box encountered.')
        select_name = select \
            .find_element_by_css_selector('input[type="hidden"]') \
            .get_attribute('name')
        for option in self.iterate_react_select_options(select):
            if option.text == data[select_name]:
                option.click()
                break
        else:
            raise MissingDataException('Option not found.')

    def fill_checkbox(self, input_el: WebElement, values) -> None:
        """Select checkbox in case it is required or uncheck otherwise"""
        should_be_selected = input_el.get_attribute("value") in values
        if should_be_selected and not input_el.is_selected():
            input_el.click()

    @staticmethod
    def select_first(driver: webdriver.Remote, select: WebElement) -> None:
        # TODO: this class should have driver as a property
        select.click()
        ActionChains(driver).send_keys(Keys.ENTER).perform()

    @staticmethod
    def select_first_from_dropdown(driver: webdriver.Remote,
                                   select: WebElement) -> None:
        select.click()
        ActionChains(driver).send_keys(Keys.ARROW_DOWN).perform()

    def get_form_inputs(self, form: WebElement) -> t.Iterable[WebElement]:
        inputs_selector = ('input:not(.hidden):not([type="hidden"])'
                           ':not([type="submit"])')
        return filter(
            self.get_input_name,
            form.find_elements_by_css_selector(inputs_selector))

    def get_form_textareas(self, form: WebElement) -> t.Iterable[WebElement]:
        selector = 'textarea:not(.hidden):not([type="hidden"])'
        return filter(
            self.get_input_name,
            form.find_elements_by_css_selector(selector))

    def fill_form(self, form: WebElement, **data: InputValue) -> None:
        for form_input in self.get_form_inputs(form):
            self.fill_input(form_input, **data)

        for textarea in self.get_form_textareas(form):
            self.fill_input(textarea, **data)

    def submit_form(self, form: WebElement) -> None:
        submit_selector = 'button[type="submit"], input[type="submit"]'
        form.find_element_by_css_selector(submit_selector).click()

    def fill_form_and_submit(self,
                             form_selector: str,
                             **data: InputValue) -> None:
        """Uniform method filling and submitting form.

        Example parameters:
        form_selector = '#data-form'
        data = {
            'name': 'Name',
            'phone': 123456789,
            'country': 'US',
        }
        """
        form = self.wait_for_element(form_selector)
        self.fill_form(form, **data)
        self.submit_form(form)
