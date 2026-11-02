"""
Author: Karim Elkholy
Tester: Karim Elkholy

T007 - Wish List (F7) - all 4 scenarios.

Function IDs/Names: F7 Wish List
(heart button on a product page, saved products at
https://opencart.abstracta.us/index.php?route=account/wishlist)

Scenario 1: a guest clicking the heart is asked to log in first.
Scenario 2: a logged-in user saves the iPhone from its product page; it
            appears on the My Wish List page and the header shows
            'Wish List (1)'.
Scenario 3: removing the product empties the wish list again
            (success message and 'Wish List (0)').
Scenario 4: a guest opening the wish list URL directly is redirected to
            the login page.

Depends on: F1 User Login -> F7 Wish List (scenarios 2 and 3 need a
session). Each scenario registers its own fresh account; OpenCart logs
new customers in automatically, so wish-list edits never leak into
another test case's session (same pattern as T012).

Drafted with AI assistance (Claude) and reviewed by the author.
"""
import uuid
from collections.abc import Callable
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver

from pages.login_page import LoginPage
from pages.product_page import ProductPage
from pages.register_page import RegisterPage
from pages.wishlist_page import WishlistPage

TEST_ID = "T007"
TEST_PASSWORD = "S3cure!Pass2026"


def _unique_email() -> str:
    return f"t007.{uuid.uuid4().hex[:8]}@example.com"


def _register(driver: WebDriver, base_url: str, email: str) -> None:
    """
    Register `email`; OpenCart logs the new customer in automatically.
    """
    RegisterPage(driver, base_url).open().register(
        "Karim", "Tester", email, "+61400000000", TEST_PASSWORD
    )


def test_scenario_1_guest_cannot_save_to_wish_list(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    # No login: open the iPhone page straight away.
    product = ProductPage(driver, base_url).open()
    product.add_to_wishlist()
    snap("t007_scenario_1")

    # Guests are asked to log in instead of saving the product.
    message = product.toast_text().lower()
    assert "must login or create an account" in message, (
        f"expected the login prompt for a guest, got {product.toast_text()!r}"
    )
    assert "added iphone to your wish list" not in message, (
        "a guest must not be able to save the product"
    )


def test_scenario_2_logged_in_user_saves_product(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    _register(driver, base_url, _unique_email())

    # Click the heart on the iPhone product page.
    product = ProductPage(driver, base_url).open().add_to_wishlist()
    assert "added iPhone to your wish list" in product.toast_text(), (
        f"expected the saved confirmation, got {product.toast_text()!r}"
    )
    # The header counter reflects the saved product straight away.
    assert product.wishlist_count_text() == "Wish List (1)", (
        f"header should show 'Wish List (1)', got {product.wishlist_count_text()!r}"
    )
    snap("t007_scenario_2")

    # The saved product shows up on the My Wish List page.
    wishlist = WishlistPage(driver, base_url).open()
    assert wishlist.has_product("iPhone"), (
        f"iPhone should be on the wish list, got {wishlist.product_names()!r}"
    )


def test_scenario_3_remove_product_from_wish_list(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    _register(driver, base_url, _unique_email())
    ProductPage(driver, base_url).open().add_to_wishlist()

    wishlist = WishlistPage(driver, base_url).open()
    assert wishlist.has_product("iPhone")

    wishlist.remove("iPhone")
    assert "modified your wish list" in wishlist.success_text(), (
        f"expected the removal confirmation, got {wishlist.success_text()!r}"
    )
    # The header counter drops back to zero with the row gone.
    assert wishlist.wishlist_count_text() == "Wish List (0)", (
        f"header should show 'Wish List (0)', got {wishlist.wishlist_count_text()!r}"
    )
    snap("t007_scenario_3")
    assert not wishlist.has_product("iPhone"), (
        f"iPhone should be removed, got {wishlist.product_names()!r}"
    )


def test_scenario_4_guest_wishlist_url_redirects_to_login(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    # No login: open the wish list URL directly.
    WishlistPage(driver, base_url).open()
    snap("t007_scenario_4")

    # The wish list is protected: the guest lands on the login page.
    assert LoginPage(driver, base_url).is_loaded(), (
        "a guest opening the wish list URL must be redirected to the login page"
    )
