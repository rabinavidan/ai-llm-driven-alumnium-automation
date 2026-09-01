"""
Shared pytest fixtures and Allure integration.

Design notes
------------
* `driver` builds either a local Chrome (nice for a live, headed demo) or a
  RemoteWebDriver pointed at the dockerized `selenium/standalone-chromium`,
  selected purely by the SELENIUM_URL env var. No code change to switch.
* `al` wraps that driver in an Alumnium session. Alumni.quit() tears down both
  the AI session and the underlying driver, so teardown is idempotent.
* A `pytest_runtest_makereport` hook attaches a screenshot + page source to the
  Allure report on any failure — the kind of forensic trail an SDET report needs.
"""
import os
import platform
from pathlib import Path

import allure
import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

from alumnium import Alumni

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://www.saucedemo.com")
SELENIUM_URL = os.getenv("SELENIUM_URL", "").strip()
ALLURE_DIR = Path("allure-results")


def _chrome_options() -> ChromeOptions:
    opts = ChromeOptions()
    # Headless in CI/containers; flip HEADLESS=false locally to watch the AI drive.
    if os.getenv("HEADLESS", "true").lower() == "true":
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1440,900")
    return opts


@pytest.fixture
def driver():
    """A Selenium driver — remote (docker) if SELENIUM_URL is set, else local Chrome."""
    if SELENIUM_URL:
        drv = webdriver.Remote(command_executor=SELENIUM_URL, options=_chrome_options())
    else:
        drv = webdriver.Chrome(options=_chrome_options())
    drv.set_page_load_timeout(60)
    yield drv
    try:
        drv.quit()  # harmless if Alumni already quit it
    except Exception:
        pass


@pytest.fixture
def al(driver):
    """An Alumnium session over the driver. Owns the AI teardown."""
    instance = Alumni(driver)
    yield instance
    try:
        instance.quit()
    except Exception:
        pass


@pytest.fixture
def base_url() -> str:
    return BASE_URL


# --------------------------------------------------------------------------- #
# Allure: attach forensic evidence on failure                                 #
# --------------------------------------------------------------------------- #
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        drv = item.funcargs.get("driver")
        if drv is not None:
            try:
                allure.attach(
                    drv.get_screenshot_as_png(),
                    name="failure-screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
                allure.attach(
                    drv.page_source,
                    name="page-source",
                    attachment_type=allure.attachment_type.HTML,
                )
                allure.attach(
                    drv.current_url,
                    name="url",
                    attachment_type=allure.attachment_type.TEXT,
                )
            except Exception:
                pass


# --------------------------------------------------------------------------- #
# Allure: write environment metadata so the report header is populated         #
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session", autouse=True)
def _allure_environment():
    ALLURE_DIR.mkdir(parents=True, exist_ok=True)
    props = {
        "SUT": BASE_URL,
        "AI.Provider": os.getenv("ALUMNIUM_MODEL", "ollama"),
        "Ollama.URL": os.getenv("ALUMNIUM_OLLAMA_URL", "n/a"),
        "Selenium": SELENIUM_URL or "local-chrome",
        "Python": platform.python_version(),
        "OS": f"{platform.system()} {platform.release()}",
    }
    (ALLURE_DIR / "environment.properties").write_text(
        "\n".join(f"{k}={v}" for k, v in props.items())
    )
    yield
