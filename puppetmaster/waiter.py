import os
import itertools
import typing as t

from django.conf import settings
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException)

from .core import BasePuppetMaster

STALE_ELEMENT_DEFAULT_RETRIES = 3


class WaiterInterface(BasePuppetMaster):
    def _wait(self,
              condition: t.Callable[[webdriver.Remote], t.Any],
              timeout: int) -> WebDriverWait:
        raise NotImplementedError

    def wait(self,
             condition: t.Callable[[webdriver.Remote], t.Any],
             timeout: int = 1) -> WebDriverWait:
        raise NotImplementedError

    def wait_for_elements(self, selector: str, timeout: int = 1) -> WebDriverWait:
        raise NotImplementedError

    def wait_for_element(self, selector: str, timeout: int = 1) -> WebDriverWait:
        raise NotImplementedError

    def make_screenshot(self, id_iter: t.Iterator[int] = itertools.count(0)):
        raise NotImplementedError


class WaiterMixin(WaiterInterface):
    def make_screenshot(self, id_iter: t.Iterator[int] = itertools.count(0)):
        filename = (f'{settings.PM__DEFAULT_SCREENSHOT_DIR}'
                    f'puppet_master_{os.getpid()}_{next(id_iter)}.png')
        self.driver.get_screenshot_as_file(filename)

    def _wait(self,
              condition: t.Callable[[webdriver.Remote], t.Any],
              timeout: int) -> WebDriverWait:
        try:
            return WebDriverWait(
                self.driver,
                timeout=timeout,
                poll_frequency=0.05
            ).until(condition)
        except TimeoutException as e:
            # Take screenshot before failure and explicitly re-raise exception
            self.make_screenshot()
            raise e

    def wait(self,
             condition: t.Callable[[webdriver.Remote], t.Any],
             timeout: int = 1,
             max_tries: int = STALE_ELEMENT_DEFAULT_RETRIES) -> WebDriverWait:
        if max_tries == 0:
            raise TimeoutException
        try:
            return self._wait(condition, timeout)
        except StaleElementReferenceException:
            return self.wait(condition, timeout, max_tries - 1)

    def wait_for_element(self, selector: str, timeout: int = 1) -> WebDriverWait:
        return self.wait(lambda driver: driver.find_element_by_css_selector(
            selector
        ), timeout)

    def wait_for_elements(self, selector: str, timeout: int = 1) -> WebDriverWait:
        return self.wait(lambda driver: driver.find_elements_by_css_selector(
            selector,
        ), timeout)
