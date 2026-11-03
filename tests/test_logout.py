"""
Author: Karim Elkholy
Tester: Karim Elkholy

T009 - Logout (F9) - all 3 scenarios.

Function IDs/Names: F9 Logout
(My account > Logout, confirmation page at
https://opencart.abstracta.us/index.php?route=account/logout)

Scenario 1: a logged-in user logs out and gets the confirmation page;
            the My account menu offers only Register and Login afterwards.
Scenario 2: account pages (dashboard, wish list) require logging in
            again after logging out.
Scenario 3: a guest opening the logout URL directly gets the
            confirmation page safely and no session is created.

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
from pages.logout_page import LogoutPage
from pages.register_page import RegisterPage
from pages.wishlist_page import WishlistPage

TEST_ID = "T009"
TEST_PASSWORD = "S3cure!Pass2026"

# The My account dropdown offers exactly these two entries to a guest.
GUEST_MENU_ROUTES: set[str] = {"account/register", "account/login"}


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


def test_scenario_1_successful_logout(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    base = _register_logged_in(driver, base_url)

    # My account > Logout.
    base.logout()
    logout = LogoutPage(driver, base_url)
    snap("t009_scenario_1")

    assert logout.shows_confirmation(), "should land on the logout confirmation page"
    routes = base.my_account_menu_routes()
    assert set(routes) == GUEST_MENU_ROUTES, (
        f"after logout the menu should offer only Register/Login, got {routes!r}"
    )


def test_scenario_2_account_pages_locked_after_logout(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    base = _register_logged_in(driver, base_url)
    base.logout()
    login = LoginPage(driver, base_url)

    # The account dashboard bounces back to the login page...
    AccountPage(driver, base_url).open()
    assert login.is_loaded(), "the account dashboard must require logging in again"

    # ...and so does the wish list.
    WishlistPage(driver, base_url).open()
    snap("t009_scenario_2")
    assert login.is_loaded(), "the wish list must require logging in again"


def test_scenario_3_logout_url_opened_as_guest(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    # No login: open the logout URL directly.
    logout = LogoutPage(driver, base_url).open()
    base = BasePage(driver, base_url)

    # The request is handled safely: the logged-off page is shown.
    assert logout.shows_confirmation(), (
        "the logout page should load for a guest without an error"
    )
    routes = base.my_account_menu_routes()
    assert set(routes) == GUEST_MENU_ROUTES, (
        f"a guest's menu should offer only Register/Login, got {routes!r}"
    )

    # No session was created: account pages still require logging in.
    AccountPage(driver, base_url).open()
    snap("t009_scenario_3")
    assert LoginPage(driver, base_url).is_loaded(), (
        "opening the logout URL as a guest must not create a session"
    )
