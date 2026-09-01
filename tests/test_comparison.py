"""
THE showcase test — brittle selectors vs. AI intent, side by side.

Run this in the interview. Both tests perform the identical journey (log in →
add backpack → verify cart = 1). One is tied to specific DOM ids/classes; the
other describes intent. Then talk to the failure mode:

    In the classic version, the day a developer renames `add-to-cart-sauce-labs-backpack`
    or restructures `.shopping_cart_badge`, the test goes red and someone spends an
    afternoon re-hunting selectors. The Alumnium version keeps passing because it
    reasons over the accessibility tree, not over a frozen locator.

To make that point *live* on a mutable app, point BASE_URL at an app you control,
change a class name between the two runs, and watch only the classic test break.
"""
import allure
import pytest

from tests.ai_steps import ai_check, ai_do
from tests.pages.inventory_page import LoginPage


@allure.epic("SauceDemo")
@allure.feature("Resilience — classic vs AI")
class TestComparison:

    @pytest.mark.classic
    @allure.story("Classic selector-based journey (the maintenance liability)")
    def test_add_to_cart_classic(self, driver, base_url):
        inventory = LoginPage(driver, base_url).open().login("standard_user", "secret_sauce")
        with allure.step("Assert inventory title via .title selector"):
            assert "Products" in inventory.title_text()
        with allure.step("Add backpack via #add-to-cart-sauce-labs-backpack"):
            inventory.add_backpack_to_cart()
        with allure.step("Read cart via .shopping_cart_badge selector"):
            assert inventory.cart_count() == 1

    @pytest.mark.ai
    @allure.story("Same journey as intent (self-describing, selector-free)")
    def test_add_to_cart_ai(self, al, driver, base_url):
        driver.get(base_url)
        ai_do(al, "log in as 'standard_user' with password 'secret_sauce'")
        ai_check(al, "the products page is displayed")
        ai_do(al, "add the 'Sauce Labs Backpack' to the shopping cart")
        ai_check(al, "the cart shows exactly 1 item")
