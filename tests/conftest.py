"""
Author: Karim Elkholy

Shared fixtures for the Selenium web test suite (driver, screenshots, test account).

Environment variables:
    BASE_URL  -- base of the site under test
                 (default: https://opencart.abstracta.us/index.php)
    HEADLESS  -- "1" to run Chrome headless, anything else shows the browser
                 (default: "0")
"""
import os
import sys
import uuid
from collections.abc import Callable, Iterator
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

# Make the top-level `pages` package importable when pytest is run from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pages.base_page import BasePage  # noqa: E402
from pages.register_page import RegisterPage  # noqa: E402

REPO_ROOT: Path = Path(__file__).resolve().parents[1]
BASE_URL: str = os.environ.get(
    "BASE_URL", "https://opencart.abstracta.us/index.php"
)
SCREENSHOT_DIR: Path = REPO_ROOT / "artifacts" / "screenshots"

TEST_ACCOUNT_PASSWORD: str = "S3cure!Pass2026"


def make_driver() -> WebDriver:
    opts = webdriver.ChromeOptions()
    if os.environ.get("HEADLESS", "0") == "1":
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    # The shared demo's Let's Encrypt cert sometimes lapses between the site
    # admin's renewals (it expired 2026-11-02 overnight); these tests target
    # OpenCart's behaviour, not TLS, so tolerate a stale certificate instead
    # of failing every test with Chrome's 'Privacy error' page.
    opts.add_argument("--ignore-certificate-errors")
    return webdriver.Chrome(options=opts)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]) -> Any:
    """
    Record each phase's report on the item so fixtures can see failures.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture
def driver() -> Iterator[WebDriver]:
    """
    One fresh Chrome window per test, closed afterwards.
    """
    d: WebDriver = make_driver()
    yield d
    d.quit()


@pytest.fixture(autouse=True)
def screenshot_on_failure(request: pytest.FixtureRequest) -> Iterator[None]:
    """
    Save a screenshot automatically when a test that uses the browser fails.

        The driver is only picked up if the test already asked for it, so tests
        that never touch the browser stay lightweight.
    """
    yield
    report = getattr(request.node, "rep_call", None)
    driver: WebDriver | None = request.node.funcargs.get("driver")
    if report is not None and report.failed and driver is not None:
        try:
            folder: Path = _screenshot_folder(request)
            stamp: str = datetime.now().strftime("%H%M%S")
            driver.save_screenshot(str(folder / f"{stamp}_FAILED.png"))
        except Exception:
            pass  # browser already gone; never mask the real test failure


def _screenshot_folder(request: pytest.FixtureRequest) -> Path:
    folder: Path = SCREENSHOT_DIR / request.node.name
    folder.mkdir(parents=True, exist_ok=True)
    return folder


@pytest.fixture
def snap(driver: WebDriver, request: pytest.FixtureRequest) -> Callable[[str], Path]:
    """
    snap("t001_scenario_1") saves a screenshot of the current page for the
    report, filed under the test case's TEST_ID folder. Filenames are stable,
    so re-running the suite overwrites yesterday's evidence in place.
    """
    test_id: str = getattr(request.module, "TEST_ID", "misc")

    def _snap(name: str) -> Path:
        folder: Path = SCREENSHOT_DIR / test_id
        folder.mkdir(parents=True, exist_ok=True)
        path: Path = folder / f"{name}.png"
        driver.save_screenshot(str(path))
        return path

    return _snap


@pytest.fixture(scope="session")
def registered_user() -> Iterator[dict[str, str]]:
    """
    A unique account registered through the real registration page.

        Runs once per test session: registers the account, logs out again, then
        hands the credentials to every login test that needs an existing user.
    """
    driver: WebDriver = make_driver()
    try:
        base = BasePage(driver, BASE_URL)
        email: str = f"autotest.{uuid.uuid4().hex[:8]}@example.com"
        register = RegisterPage(driver, BASE_URL).open()
        register.register("Auto", "Tester", email, "+61400000000", TEST_ACCOUNT_PASSWORD)
        base.logout()
        yield {
            "email": email,
            "password": TEST_ACCOUNT_PASSWORD,
            "first_name": "Auto",
            "last_name": "Tester",
        }
    finally:
        driver.quit()


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL
