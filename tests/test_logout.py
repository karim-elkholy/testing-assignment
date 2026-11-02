"""
Author: Karim Elkholy
Tester: Karim Elkholy

T009 - Logout (F9) - all 3 scenarios.

Function IDs/Names: F9 Logout
(My account > Logout, confirmation page at
https://opencart.abstracta.us/index.php?route=account/logout)

Scenario 1: a logged-in user logs out and gets the confirmation page.
Scenario 2: account pages require logging in again after logging out.
Scenario 3: the My account menu offers Register/Login again, not Logout.

Depends on: F1 User Login -> F9 Logout. Each scenario registers its own
fresh account; OpenCart logs new customers in automatically, so no
other test case's session is touched.

Drafted with AI assistance (Claude) and reviewed by the author.
"""
import uuid
from collections.abc import Callable
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver

from pages.account_page import AccountPage
from pages.base_page import BasePage
from pages.login_page import LoginPage
from pages.register_page import RegisterPage

TEST_ID = "T009"
TEST_PASSWORD = "S3cure!Pass2026"


def _unique_email() -> str:
    return f"t009.{uuid.uuid4().hex[:8]}@example.com"


def _register_logged_in(driver: WebDriver, base_url: str) -> BasePage:
    """
    Register a fresh account (auto-logged-in) and return the header page.
    """
    RegisterPage(driver, base_url).open().register(
        "Karim", "Tester", _unique_email(), "+61400000000", TEST_PASSWORD
    )
    return BasePage(driver, base_url)


def test_scenario_1_logout_shows_confirmation(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    base = _register_logged_in(driver, base_url)

    # My account > Logout.
    base.logout()
    snap("t009_scenario_1")

    assert "route=account/logout" in driver.current_url, "should land on the logout page"
    assert base.contains_text("logged off your account"), (
        "the confirmation page should say the user was logged off"
    )


def test_scenario_2_account_pages_require_login_again(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    base = _register_logged_in(driver, base_url)
    base.logout()

    # Opening the account dashboard after logout bounces to the login page.
    AccountPage(driver, base_url).open()
    snap("t009_scenario_2")

    assert LoginPage(driver, base_url).is_loaded(), (
        "the account dashboard must require logging in again"
    )


def test_scenario_3_menu_offers_login_again(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    base = _register_logged_in(driver, base_url)
    base.logout()

    routes = base.my_account_menu_routes()
    snap("t009_scenario_3")

    assert "account/login" in routes and "account/register" in routes, (
        f"after logout the menu should offer Register/Login again, got {routes!r}"
    )
    assert "account/logout" not in routes, (
        f"after logout the menu must not offer Logout, got {routes!r}"
    )
