"""
Author: Daniel

T007 - Wish List (F7).

Function IDs/Names: F7 Wish List
Tester: Daniel

Scenario 1: a guest tries to save a product -> asked to log in, nothing saved.
Scenario 2: a logged-in user saves a product -> success banner, counter = 1, product listed.
Scenario 3: a logged-in user removes the product -> success banner, product gone, counter = 0.
Scenario 4: a guest opens the wish list URL directly -> redirected to the login page.

Depends on F1 User Login (and F2 via the `registered_user` fixture): saving a
wish list needs a logged-in session, so T007 runs after T001/T002 pass.
Product under test: iPhone (product_id=40).
"""
from collections.abc import Callable
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver

from pages.account_page import AccountPage
from pages.login_page import LoginPage
from pages.wishlist_page import WishListPage

TEST_ID = "T007"

IPHONE_ID: int = 40


def _login(driver: WebDriver, base_url: str, user: dict[str, str]) -> None:
    """Log in with the session's test account and confirm the dashboard loaded."""
    LoginPage(driver, base_url).open().login(user["email"], user["password"])
    assert AccountPage(driver, base_url).is_loaded(), "precondition: login must succeed"


def test_scenario_1_guest_cannot_save_to_wishlist(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    wishlist = WishListPage(driver, base_url)

    # Input: guest (not logged in) clicks 'Add to Wish List' on the iPhone page.
    banner: str = wishlist.add_from_product_page(IPHONE_ID)
    snap("t007_scenario_1")

    # Expected output: the site asks the guest to log in or register first.
    assert "You must login or create an account to save iPhone to your wish list!" in banner, banner
    # The visitor stays on the product page (no silent redirect).
    assert "product_id=40" in driver.current_url


def test_scenario_2_logged_in_user_saves_product(
    driver: WebDriver,
    base_url: str,
    snap: Callable[[str], Path],
    registered_user: dict[str, str],
) -> None:
    _login(driver, base_url, registered_user)
    wishlist = WishListPage(driver, base_url)

    # Input: logged-in user clicks 'Add to Wish List' on the iPhone page.
    banner: str = wishlist.add_from_product_page(IPHONE_ID)
    snap("t007_scenario_2_1")

    # Expected output 1: success banner and the header counter shows 1 item.
    assert "Success: You have added iPhone to your wish list!" in banner, banner
    assert wishlist.header_total() == "Wish List (1)", wishlist.header_total()

    # Expected output 2: the iPhone is listed on the My Wish List page.
    wishlist.open()
    snap("t007_scenario_2_2")
    assert "iPhone" in wishlist.product_names()


def test_scenario_3_logged_in_user_removes_product(
    driver: WebDriver,
    base_url: str,
    snap: Callable[[str], Path],
    registered_user: dict[str, str],
) -> None:
    _login(driver, base_url, registered_user)
    wishlist = WishListPage(driver, base_url)

    # Self-contained: make sure the iPhone is in the wish list before removing it.
    wishlist.add_from_product_page(IPHONE_ID)
    wishlist.open()
    assert "iPhone" in wishlist.product_names(), "precondition: iPhone must be listed"

    # Input: click the red 'Remove' (X) button beside the iPhone.
    banner: str = wishlist.remove(IPHONE_ID)
    snap("t007_scenario_3")

    # Expected output: success banner, iPhone gone, header counter back to 0.
    assert "Success: You have modified your wish list!" in banner, banner
    assert "iPhone" not in wishlist.product_names()
    assert wishlist.header_total() == "Wish List (0)", wishlist.header_total()


def test_scenario_4_guest_wishlist_url_redirects_to_login(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    # Input: a guest types the wish list URL straight into the address bar.
    WishListPage(driver, base_url).open()
    snap("t007_scenario_4")

    # Expected output: access is refused and the guest lands on the login page.
    assert "route=account/login" in driver.current_url, driver.current_url
    assert LoginPage(driver, base_url).find(LoginPage.EMAIL).is_displayed()
