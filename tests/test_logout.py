"""
Author: Daniel

T009 - Logout (F9).

Function IDs/Names: F9 Logout
Tester: Daniel

Scenario 1: a logged-in user logs out via My Account > Logout -> confirmation page,
            header switches back to Login/Register.
Scenario 2: after logging out, protected pages (My Account, Wish List) redirect to login.
Scenario 3: a guest who was never logged in opens the logout URL -> handled safely,
            no session is created and protected pages stay locked.

Depends on F1 User Login (and F2 via the `registered_user` fixture), so T009 runs
after T001/T002 pass. Each test opens a fresh browser (no shared session).
"""
from collections.abc import Callable
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver

from pages.account_page import AccountPage
from pages.base_page import BasePage
from pages.login_page import LoginPage
from pages.logout_page import LOGGED_OFF_MESSAGE, LogoutPage
from pages.wishlist_page import WishListPage

TEST_ID = "T009"


def _login(driver: WebDriver, base_url: str, user: dict[str, str]) -> None:
    """Log in with the session's test account and confirm the dashboard loaded."""
    LoginPage(driver, base_url).open().login(user["email"], user["password"])
    assert AccountPage(driver, base_url).is_loaded(), "precondition: login must succeed"


def test_scenario_1_successful_logout(
    driver: WebDriver,
    base_url: str,
    snap: Callable[[str], Path],
    registered_user: dict[str, str],
) -> None:
    _login(driver, base_url, registered_user)

    # Input: open the 'My Account' dropdown and click 'Logout'.
    BasePage(driver, base_url).logout()  # waits until the URL contains account/logout
    logout = LogoutPage(driver, base_url)
    snap("t009_scenario_1_1")

    # Expected output 1: the logout confirmation message is shown.
    assert LOGGED_OFF_MESSAGE in logout.message(), logout.message()
    # Expected output 2: header menu now offers Login/Register and no Logout.
    assert logout.header_shows_guest_menu(), "header should show the guest menu after logout"
    snap("t009_scenario_1_2")


def test_scenario_2_protected_pages_locked_after_logout(
    driver: WebDriver,
    base_url: str,
    snap: Callable[[str], Path],
    registered_user: dict[str, str],
) -> None:
    _login(driver, base_url, registered_user)
    BasePage(driver, base_url).logout()

    # Input 1: try to reopen the My Account dashboard directly by URL.
    AccountPage(driver, base_url).open()
    snap("t009_scenario_2_1")
    # Expected output 1: redirected to the login page - the old session is gone.
    assert "route=account/login" in driver.current_url, driver.current_url

    # Input 2: try to open the Wish List directly by URL.
    WishListPage(driver, base_url).open()
    snap("t009_scenario_2_2")
    # Expected output 2: also redirected to the login page.
    assert "route=account/login" in driver.current_url, driver.current_url


def test_scenario_3_logout_url_as_guest(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    # Input: a guest (never logged in) types the logout URL into the address bar.
    logout = LogoutPage(driver, base_url).open()
    snap("t009_scenario_3_1")

    # Expected output 1: the page loads without an error and the visitor stays a guest.
    assert LOGGED_OFF_MESSAGE in logout.message(), logout.message()
    assert logout.header_shows_guest_menu(), "visitor should still be shown as a guest"

    # Expected output 2: no session was created - My Account still redirects to login.
    AccountPage(driver, base_url).open()
    snap("t009_scenario_3_2")
    assert "route=account/login" in driver.current_url, driver.current_url
