"""
Login journeys expressed as intent — no selectors, no waits.

Notice there is not a single By.ID, CSS selector, or explicit wait in this file.
The steps read like a manual test case, yet they execute autonomously.
"""
import allure
import pytest

from tests.ai_steps import ai_check, ai_do


@allure.epic("SauceDemo")
@allure.feature("Authentication")
class TestLogin:

    @pytest.mark.ai
    @pytest.mark.smoke
    @allure.story("Valid user can sign in")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_standard_user_logs_in(self, al, driver, base_url):
        driver.get(base_url)
        ai_do(al, "log in as 'standard_user' with password 'secret_sauce'")
        ai_check(al, "the products / inventory page is displayed")
        ai_check(al, "the page shows a list of purchasable products")

    @pytest.mark.ai
    @allure.story("Locked-out user is rejected")
    @allure.severity(allure.severity_level.NORMAL)
    def test_locked_out_user_is_blocked(self, al, driver, base_url):
        driver.get(base_url)
        ai_do(al, "attempt to log in as 'locked_out_user' with password 'secret_sauce'")
        ai_check(al, "an error message explains that this user has been locked out")
        ai_check(al, "the products page is NOT displayed")
