"""
Author: Monark
Tester: Monark

T015 - Checkout (F15) - all 3 scenarios.

Function IDs/Names: F15 Checkout
(https://opencart.abstracta.us/index.php?route=checkout/checkout)
Depends on: F4 Shopping Cart (checkout needs a product in the cart).

Scenario 1: opening checkout with an empty cart redirects to the empty cart.
Scenario 2: guest checkout with empty billing details is blocked by field errors.
Scenario 3: the order is blocked when Terms & Conditions are not accepted.

Each scenario is self-contained: it adds the iPhone to the cart itself.
"""
import uuid
from collections.abc import Callable
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver

from pages.cart_page import EMPTY_MESSAGE
from pages.checkout_page import CheckoutPage
from pages.product_page import ProductPage

TEST_ID = "T015"

# Valid guest billing details used in Scenario 3 (unique email each run).
GUEST_DETAILS: dict[str, str] = {
    "first_name": "Test",
    "last_name": "User",
    "email": f"checkout.{uuid.uuid4().hex[:8]}@example.com",
    "telephone": "0400000000",
    "address_1": "1 Test Street",
    "city": "Sydney",
    "postcode": "2000",
    "country": "Australia",
    "region": "New South Wales",
}


def _checkout_with_iphone(driver: WebDriver, base_url: str) -> CheckoutPage:
    """Add the iPhone to the cart (F4), then open the checkout page."""
    ProductPage(driver, base_url).open().add_to_cart()
    checkout = CheckoutPage(driver, base_url).open()
    # If the site sends us back to the cart, the product cannot be checked
    # out (see Defect 3 - stock warning); fail with a clear explanation.
    assert checkout.is_on_checkout(), (
        f"checkout redirected to {driver.current_url} - product could not proceed to checkout (see Defect 3)"
    )
    return checkout


def test_scenario_1_empty_cart_redirects_to_cart(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    # Go straight to checkout without adding anything to the cart.
    checkout = CheckoutPage(driver, base_url).open()
    checkout.wait.until(lambda d: "checkout/cart" in d.current_url)
    snap("t015_scenario_1")

    assert "checkout/cart" in driver.current_url, "empty cart should redirect to the cart page"
    assert checkout.contains_text(EMPTY_MESSAGE), f"expected '{EMPTY_MESSAGE}' on the cart page"


def test_scenario_2_empty_billing_details_blocked(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    checkout = _checkout_with_iphone(driver, base_url)

    # Step 1: Guest Checkout. Step 2: leave every field empty and continue.
    checkout.choose_guest_checkout()
    checkout.continue_billing()
    errors: list[str] = checkout.field_errors()
    snap("t015_scenario_2")

    joined: str = " ".join(errors).lower()
    # Each required field shows its own message.
    assert "first name must be between 1 and 32 characters" in joined, f"missing first-name error: {errors!r}"
    assert "last name must be between 1 and 32 characters" in joined, f"missing last-name error: {errors!r}"
    assert "e-mail address does not appear to be valid" in joined, f"missing email error: {errors!r}"
    # The form stays on Step 2, so checkout cannot continue.
    assert checkout.is_on_checkout()


def test_scenario_3_terms_not_accepted_blocks_order(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    checkout = _checkout_with_iphone(driver, base_url)

    # Step 1 and Step 2: guest checkout with valid billing details.
    checkout.choose_guest_checkout()
    checkout.fill_billing(GUEST_DETAILS)
    checkout.continue_billing()
    # Step 4: accept the default delivery method.
    checkout.continue_delivery_method()
    # Step 5: continue WITHOUT ticking Terms & Conditions.
    warning: str = checkout.continue_payment_without_agreeing()
    snap("t015_scenario_3")

    assert "you must agree to the terms & conditions" in warning.lower(), (
        f"expected Terms & Conditions warning, got {warning!r}"
    )
