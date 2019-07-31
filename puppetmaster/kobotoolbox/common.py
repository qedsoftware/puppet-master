from django.conf import settings
from registration.models import RegistrationProfile
from puppetmaster.common import SeleniumTestsMixin


class Urls:
    LOGIN = "/accounts/login/"
    CREATE_ACCOUNT = "/accounts/register/"
    ACCOUNT_SETTINGS = "/#/account-settings"


class KobotoolboxSeleniumMixin(SeleniumTestsMixin):
    """
    Wrapper for kobotoolbox-specific functions
    """
    ENKETO_FORM_SELECTOR = '.main .paper form'

    def log_in_as_user(self, username: str, password: str) -> None:
        self.driver.get(settings.KPI_ADDR + Urls.LOGIN)
        self.fill_form_and_submit(
            '.registration.registration--login',
            username=username, password=password)

    @staticmethod
    def verify_email(username: str) -> None:
        reg_profile = RegistrationProfile.objects.get(user__username=username)
        reg_profile.activated = True
        reg_profile.save()

    def select_form(self, form_name: str) -> None:
        assets_list_el = self.wait_for_element(".asset-list")
        form_selector = ("//*[contains(@class,'asset-items')]"
                         "//*[text()='{}']".format(form_name))
        desired_form = assets_list_el.find_element_by_xpath(form_selector)
        desired_form_link = desired_form.find_element_by_xpath('../../../a')
        desired_form_link.click()

    def select_tab_in_form_view(self, tab_name: str) -> None:
        tab_selector = ("//*[contains(@class,'form-view__toptabs')]"
                        "//*[text()='{}']".format(tab_name))
        tabs = self.wait_for_element(".form-view__toptabs")
        tabs.find_element_by_xpath(tab_selector).click()

    def select_side_tab_in_form_view(self, tab_name: str) -> None:
        tab_selector = ("//*[contains(@class,'form-view__sidetabs')]"
                        "//*[text()='{}']".format(tab_name))
        self.driver.find_element_by_xpath(tab_selector).click()
