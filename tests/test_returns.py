"""
Author: Daniel

T016 - Product Returns (F16).

Function IDs/Names: F16 Product Returns
Tester: Daniel

Scenario 1: valid return request -> 'Thank you for submitting your return request.'
Scenario 2: empty form -> one error per required field, no request sent.
Scenario 3: boundary values (invalid email, 2-digit telephone, 1-character product
            name and code) -> email and telephone rejected. Marked xfail: the site
            ACCEPTS a 1-character product name/code although its own message says
            they must be 'greater than 3' characters (reported as a defect).

Black-box techniques: equivalence partitioning (valid / empty / invalid input) and
boundary value analysis (telephone min 3, product name/code min per the message).
No login needed, so T016 has no prerequisite function.
"""
from collections.abc import Callable
from pathlib import Path

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from pages.returns_page import SUCCESS_MESSAGE, ReturnsPage

TEST_ID = "T016"

# A complete, valid request (iPhone, model 'product 11', from the demo catalogue).
VALID: dict[str, str] = {
    "firstname": "Daniel",
    "lastname": "Tester",
    "email": "daniel.tester@example.com",
    "telephone": "0400000000",
    "order_id": "1001",
    "date_ordered": "2026-10-20",
    "product": "iPhone",
    "model": "product 11",
    "comment": "Automated test - screen does not turn on.",
}


def test_scenario_1_valid_return_request(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    returns = ReturnsPage(driver, base_url).open()

    # Input: every required field valid, reason 'Dead On Arrival'.
    returns.fill(VALID, reason="Dead On Arrival")
    snap("t016_scenario_1_1")
    returns.submit()
    snap("t016_scenario_1_2")

    # Expected output: success page with the confirmation message.
    assert "account/return/success" in driver.current_url, driver.current_url
    assert SUCCESS_MESSAGE in returns.content_text()


def test_scenario_2_empty_form_rejected(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    returns = ReturnsPage(driver, base_url).open()

    # Input: submit without filling anything in.
    returns.submit()
    snap("t016_scenario_2")
    errors = returns.errors()

    # Expected output: stays on the form, one message per required field.
    assert "account/return/add" in driver.current_url, driver.current_url
    assert errors["firstname"] == "First Name must be between 1 and 32 characters!"
    assert errors["lastname"] == "Last Name must be between 1 and 32 characters!"
    assert errors["email"] == "E-Mail Address does not appear to be valid!"
    assert errors["telephone"] == "Telephone must be between 3 and 32 characters!"
    assert errors["order_id"] == "Order ID required!"
    assert errors["return_reason_id"] == "You must select a return product reason!"


@pytest.mark.xfail(
    strict=True,
    reason="Defect: 1-character Product Name/Code accepted although the message says "
    "they must be 'greater than 3' characters",
)
def test_scenario_3_boundary_values_rejected(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    returns = ReturnsPage(driver, base_url).open()

    # Input: invalid values on or just past each boundary.
    invalid = VALID | {
        "email": "daniel.tester@",  # no domain -> invalid email partition
        "telephone": "12",          # 2 chars, one below the minimum of 3
        "product": "X",             # 1 char, below the stated minimum
        "model": "Y",               # 1 char, below the stated minimum
    }
    returns.fill(invalid, reason="Dead On Arrival").submit()
    snap("t016_scenario_3")
    errors = returns.errors()

    # Expected output 1 (passes): email and telephone are rejected.
    assert errors.get("email") == "E-Mail Address does not appear to be valid!"
    assert errors.get("telephone") == "Telephone must be between 3 and 32 characters!"
    # Expected output 2 (currently fails - see xfail reason): short name/code rejected.
    assert "product" in errors, f"1-character product name was accepted: {errors}"
    assert "model" in errors, f"1-character product code was accepted: {errors}"
