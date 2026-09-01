"""
A classic, selector-driven Page Object.

This is intentionally "old school" — it exists so the demo can show the exact
same user journey written two ways: brittle selectors here vs. natural-language
intent in tests/test_comparison.py. Every locator below is a maintenance
liability the moment a developer renames a class or restructures the DOM.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    LOGIN_BTN = (By.ID, "login-button")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 15)

    def open(self):
        self.driver.get(self.base_url)
        return self

    def login(self, username, password):
        self.wait.until(EC.visibility_of_element_located(self.USERNAME)).send_keys(username)
        self.driver.find_element(*self.PASSWORD).send_keys(password)
        self.driver.find_element(*self.LOGIN_BTN).click()
        return InventoryPage(self.driver)


class InventoryPage:
    # These selectors are exactly what breaks in the real world.
    TITLE = (By.CSS_SELECTOR, ".title")
    ADD_BACKPACK = (By.ID, "add-to-cart-sauce-labs-backpack")
    CART_BADGE = (By.CSS_SELECTOR, ".shopping_cart_badge")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def title_text(self) -> str:
        return self.wait.until(EC.visibility_of_element_located(self.TITLE)).text

    def add_backpack_to_cart(self):
        self.driver.find_element(*self.ADD_BACKPACK).click()
        return self

    def cart_count(self) -> int:
        try:
            return int(self.driver.find_element(*self.CART_BADGE).text)
        except Exception:
            return 0
