"""
A full e-commerce journey in natural language, plus AI-powered data extraction.

This is the "power" test: a multi-step purchase flow that a human tester would
describe exactly like this, and an `al.get()` that pulls a *typed* value straight
off the page for a hard assertion — combining AI flexibility with deterministic
checks.
"""
import allure
import pytest

from tests.ai_steps import ai_check, ai_do, ai_get


@allure.epic("SauceDemo")
@allure.feature("Checkout")
class TestCheckout:

    @pytest.mark.ai
    @allure.story("Complete a purchase end to end")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_purchase_two_items(self, al, driver, base_url):
        driver.get(base_url)

        ai_do(al, "log in as 'standard_user' with password 'secret_sauce'")
        ai_do(al, "add the 'Sauce Labs Backpack' to the shopping cart")
        ai_do(al, "add the 'Sauce Labs Bike Light' to the shopping cart")

        ai_check(al, "the cart icon shows 2 items")

        ai_do(al, "open the shopping cart")
        ai_check(al, "the cart lists the Backpack and the Bike Light")

        ai_do(al, "proceed to checkout")
        ai_do(al, "fill the checkout form with first name 'Ada', last name 'Lovelace', and postal code '10001', then continue")

        ai_check(al, "the order summary / overview page is shown with a payment and total")

        ai_do(al, "finish the order")
        ai_check(al, "a confirmation message thanks the user for the order")

    @pytest.mark.ai
    @allure.story("Extract the cart total as structured data")
    @allure.severity(allure.severity_level.NORMAL)
    def test_extract_item_total(self, al, driver, base_url):
        driver.get(base_url)
        ai_do(al, "log in as 'standard_user' with password 'secret_sauce'")
        ai_do(al, "add the 'Sauce Labs Backpack' to the shopping cart")
        ai_do(al, "open the shopping cart")

        count = ai_get(al, "number of distinct products in the cart")
        assert count == 1, f"expected 1 product in cart, AI reported {count}"
