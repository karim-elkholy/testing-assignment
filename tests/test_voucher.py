"""
Author: Daniel

T017 - Gift Certificate Purchase (F17).

Function IDs/Names: F17 Gift Certificate Purchase
Tester: Daniel

Scenario 1: valid certificate at the upper boundary ($1000) -> success page and the
            certificate appears in the shopping cart for $1,000.00.
Scenario 2: amounts just outside the boundaries ($0.99 and $1001) -> rejected with
            'Amount must be between $1.00 and $1,000.00!'.
Scenario 3: empty form, agreement unticked -> errors for every required field and the
            'non-refundable' warning.

Black-box techniques: boundary value analysis on Amount (valid 1.00-1000.00) and
equivalence partitioning on the other fields. F17 feeds F4 Shopping Cart: a valid
certificate is added to the cart, so the cart is checked in Scenario 1.
"""
from collections.abc import Callable
from pathlib import Path

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from pages.cart_page import CartPage
from pages.voucher_page import AMOUNT_ERROR, SUCCESS_MESSAGE, VoucherPage

TEST_ID = "T017"

# Valid details reused by every scenario (only the amount changes).
VALID: dict[str, str] = {
    "to_name": "Jane Test",
    "to_email": "jane.test@example.com",
    "from_name": "Daniel Tester",
    "from_email": "daniel.tester@example.com",
    "message": "Happy testing!",
}


def test_scenario_1_valid_purchase_upper_boundary(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    voucher = VoucherPage(driver, base_url).open()

    # Input: all fields valid, theme 'General', amount 1000 (maximum allowed), agreement ticked.
    voucher.fill(**VALID, theme="General", amount="1000", agree=True)
    snap("t017_scenario_1_1")
    voucher.submit()
    snap("t017_scenario_1_2")

    # Expected output 1: confirmation page.
    assert "account/voucher/success" in driver.current_url, driver.current_url
    assert SUCCESS_MESSAGE in voucher.content_text()

    # Expected output 2: the certificate is in the cart at the full amount.
    cart = CartPage(driver, base_url).open()
    snap("t017_scenario_1_3")
    assert cart.contains_text("$1,000.00 Gift Certificate for Jane Test"), "certificate missing from cart"


@pytest.mark.parametrize("amount", ["0.99", "1001"], ids=["below_min_0.99", "above_max_1001"])
def test_scenario_2_amount_outside_boundaries_rejected(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path], amount: str
) -> None:
    voucher = VoucherPage(driver, base_url).open()

    # Input: everything valid except the amount, which is one step outside the range.
    voucher.fill(**VALID, theme="General", amount=amount, agree=True).submit()
    snap(f"t017_scenario_2_{amount.replace('.', '_')}")

    # Expected output: stays on the form with the amount range error only.
    assert "account/voucher" in driver.current_url and "success" not in driver.current_url
    assert voucher.errors() == [AMOUNT_ERROR], voucher.errors()


def test_scenario_3_empty_form_rejected(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    voucher = VoucherPage(driver, base_url).open()

    # Input: leave every field empty, no theme, agreement unticked, then Continue.
    voucher.fill("", "", "", "", theme=None, message="", amount="1", agree=False).submit()
    snap("t017_scenario_3")
    errors = voucher.errors()

    # Expected output: the non-refundable warning plus one error per required field.
    assert "You must agree that the gift certificates are non-refundable!" in voucher.warning_text()
    assert "Recipient's Name must be between 1 and 64 characters!" in errors
    assert "Your Name must be between 1 and 64 characters!" in errors
    assert errors.count("E-Mail Address does not appear to be valid!") == 2  # both emails
    assert "You must select a theme!" in errors
