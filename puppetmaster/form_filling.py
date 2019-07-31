import typing as t
import re

from selenium.common.exceptions import InvalidElementStateException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from .waiter import WaiterInterface


InputValue = t.Union[int, str, float]


class InputTypes:
    Default = 'Default'
    Date = 'Date'
    DateTime = 'DateTime'
    Checkbox = 'Checkbox'
    Time = 'Time'


class FormFillingInterface:
    def fill_input_with_value(self, input: WebElement, value: InputValue) -> None:
        raise NotImplementedError

    def fill_date_input(self, input: WebElement, value: InputValue) -> None:
        self.fill_input_with_value(input, value)

    def fill_checkbox(self, input: WebElement, value: InputValue) -> None:
        self.fill_input_with_value(input, value)

    def fill_time_input(self, input: WebElement, value: InputValue) -> None:
        self.fill_input_with_value(input, value)

    def submit_form(self, form):
        raise NotImplementedError


class FormFillingMixin(FormFillingInterface, WaiterInterface):
    @staticmethod
    def fill_input_with_value(input: WebElement, value: InputValue) -> None:
        try:
            # If element is user-editable, clear input.
            input.clear()
        except InvalidElementStateException:
            pass
        input.send_keys(value)

    @staticmethod
    def get_input_name(input: WebElement) -> str:
        return input.get_attribute('name').split('.')[-1].split('/')[-1]

    def fill_input(self, input: WebElement, **data) -> None:
        input_name = self.get_input_name(input)
        try:
            type, value = data[input_name]  # TODO: don't use keywords
        except ValueError:
            value = data[input_name]
            if re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is not None:
                type, value = InputTypes.Date, value
            elif input.get_attribute('type') in ['radio', 'checkbox']:
                type, value = InputTypes.Checkbox, [value]
            else:
                type = InputTypes.Default
        except KeyError:
            print("Form is missing '{name}' checkbox input in {data}".format(
                  name=input_name, data=""))
            return
        fill_input_map = {
            InputTypes.Date: self.fill_date_input,
            InputTypes.Default: self.fill_input_with_value,
            InputTypes.Checkbox: self.fill_checkbox,
            InputTypes.Time: self.fill_time_input,
        }
        fill_input_map[type](input, value)

    def iterate_options(self, select: WebElement) -> t.List[WebElement]:
        """Given a .Select rendered by react-select, return an iterable
        of .Select-option that can be .click()-ed to select them.
        """
        # related: https://github.com/JedWatson/react-select/issues/603#issuecomment-157888562 # noqa
        select.find_element_by_class_name('Select-arrow').click()
        self.wait(EC.element_to_be_clickable((By.CLASS_NAME, 'Select-option')))
        return select.find_elements_by_class_name('Select-option')

    def select_option(self, select: WebElement, **data):
        """Given a .Select rendered by react-select, select an option
        by _label_, not by value.
        """
        # have to first select some element to know the name of the field
        # (it is not possible to know the name of the field from the DOM if
        # nothing is selected, react-select sucks in this respect)
        for option in self.iterate_options(select):
            option.click()
            break
        else:
            raise RuntimeError('Empty select box encountered.')
        select_name = select \
            .find_element_by_css_selector('input[type="hidden"]') \
            .get_attribute('name')
        for option in self.iterate_options(select):
            if option.text == data[select_name]:
                option.click()
                break
        else:
            raise RuntimeError('Option not found.')

    def fill_checkbox(self, input: WebElement, values):
        """Select checkbox in case it is required or uncheck otherwise"""
        is_input_selected = bool(input.is_selected())
        should_be_selected = bool(input.get_attribute("value") in values)
        if should_be_selected and not is_input_selected:
            input.click()

    @staticmethod
    def select_first(driver, select: WebElement):
        # TODO: this class should have driver as a property
        select.click()
        ActionChains(driver).send_keys(Keys.ENTER).perform()

    @staticmethod
    def multi_add_remove_select_first(driver, select: WebElement):
        select.click()
        ActionChains(driver).send_keys(Keys.ARROW_DOWN).perform()

    def get_form_inputs(self, form: WebElement):
        inputs_selector = 'input:not(.hidden):not([type="hidden"])' \
                          ':not([type="submit"]):not([role="combobox"])'
        return list(filter(
            self.get_input_name,
            form.find_elements_by_css_selector(inputs_selector)))

    def get_form_textareas(self, form: WebElement):
        selector = 'textarea:not(.hidden):not([type="hidden"])'
        return list(filter(
            self.get_input_name,
            form.find_elements_by_css_selector(selector)))

    def fill_form(self, form: WebElement, **data):
        select_selector = '.Select:not(.Select--multi)'
        form_selects = form.find_elements_by_css_selector(select_selector)
        form_inputs = self.get_form_inputs(form)
        form_textareas = self.get_form_textareas(form)

        for form_input in form_inputs:
            self.fill_input(form_input, **data)

        for textarea in form_textareas:
            self.fill_input(textarea, **data)

        for form_select in form_selects:
            try:
                self.select_option(form_select, **data)
            except KeyError:
                pass

    def submit_form(self, form: WebElement) -> None:
        submit_selector = 'button[type="submit"], input[type="submit"]'
        form.find_element_by_css_selector(submit_selector).click()

    def fill_form_and_submit(self,
                             form_selector: str,
                             **data: t.Dict[str, InputValue]):
        """Uniform method filling and submitting form.

        Works both with <input> and <select>, which are located by names.
        Pass <option> value on <select>.

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
