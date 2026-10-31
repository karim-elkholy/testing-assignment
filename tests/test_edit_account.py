"""
Author: An Truong Le
Tester: An Truong Le

T012 - Edit Account Information (F12) - all 3 scenarios.

Function IDs/Names: F12 Edit Account Information
(https://opencart.abstracta.us/index.php?route=account/edit)

Scenario 1: updated last name and telephone are saved and persist.
Scenario 2: clearing the First Name shows a validation error.
Scenario 3: changing the email to one owned by another account is rejected.

Each scenario registers its own fresh account (F2 -> F1 -> F12), so edits
never touch the shared `registered_user` used by other test cases.
Drafted with AI assistance (Claude) and reviewed by the author.
"""
import uuid
from collections.abc import Callable
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver

from pages.base_page import BasePage
from pages.edit_account_page import EditAccountPage
from pages.register_page import RegisterPage

TEST_ID = "T012"
TEST_PASSWORD = "S3cure!Pass2026"


def _unique_email() -> str:
    return f"t012.{uuid.uuid4().hex[:8]}@example.com"


def _register(driver: WebDriver, base_url: str, email: str) -> None:
    """
    Register `email`; OpenCart logs the new customer in automatically.
    """
    RegisterPage(driver, base_url).open().register(
        "Truong", "Tester", email, "+61400000000", TEST_PASSWORD
    )


def test_scenario_1_successful_account_update(
    driver: WebDriver,
    base_url: str,
    snap: Callable[[str], Path],
) -> None:
    _register(driver, base_url, _unique_email())

    edit = EditAccountPage(driver, base_url).open()
    assert edit.is_loaded(), "the My Account Information page should be displayed"

    edit.update(last_name="Updated", telephone="0400123456")
    message: str = edit.success_text()  # waits for the confirmation banner
    snap("t012_scenario_1")

    assert "account/account" in driver.current_url, "should be redirected to My Account"
    assert "success" in message.lower(), f"expected account-updated confirmation, got: {message!r}"

    # The changes must persist when the form is reopened.
    edit.open()
    assert edit.value(edit.LAST_NAME) == "Updated", "last name change was not saved"
    assert edit.value(edit.TELEPHONE) == "0400123456", "telephone change was not saved"
    snap("t012_scenario_1_persisted")


def test_scenario_2_empty_first_name_rejected(
    driver: WebDriver,
    base_url: str,
    snap: Callable[[str], Path],
) -> None:
    _register(driver, base_url, _unique_email())

    edit = EditAccountPage(driver, base_url).open()
    assert edit.is_loaded(), "the My Account Information page should be displayed"

    edit.update(first_name="")  # clear the field
    errors: list[str] = edit.wait_for_field_errors()
    snap("t012_scenario_2")

    assert "First Name must be between 1 and 32 characters!" in errors, (
        f"expected first-name error, got: {errors!r}"
    )
    assert "account/edit" in driver.current_url, "should stay on the edit page"


def test_scenario_3_email_already_registered_rejected(
    driver: WebDriver,
    base_url: str,
    snap: Callable[[str], Path],
) -> None:
    # Account B owns the email we will try to take over.
    email_b = _unique_email()
    _register(driver, base_url, email_b)
    BasePage(driver, base_url).logout()

    # Account A (now logged in) tries to switch to Account B's email.
    _register(driver, base_url, _unique_email())
    edit = EditAccountPage(driver, base_url).open()
    assert edit.is_loaded(), "the My Account Information page should be displayed"

    edit.update(email=email_b)
    warning: str = edit.warning_text()
    snap("t012_scenario_3")

    assert "already registered" in warning.lower(), (
        f"expected 'already registered' warning, got: {warning!r}"
    )
    assert "account/edit" in driver.current_url, "should stay on the edit page"
