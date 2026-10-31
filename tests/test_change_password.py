"""
Author: An Truong Le
Tester: An Truong Le

T011 - Change Password (F11) - all 3 scenarios.

Function IDs/Names: F11 Change Password
(https://opencart.abstracta.us/index.php?route=account/password)

Scenario 1: a valid new password is saved and works on the next login.
Scenario 2: a mismatched password confirmation shows a validation error.
Scenario 3: a password below the 4-character minimum shows a validation error.

Each scenario registers its own fresh account (F2 -> F1 -> F11) instead of
the shared `registered_user`, so changing a password never breaks the login
tests that run in the same session.
Drafted with AI assistance (Claude) and reviewed by the author.
"""
import uuid
from collections.abc import Callable
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver

from pages.account_page import AccountPage
from pages.base_page import BasePage
from pages.change_password_page import ChangePasswordPage
from pages.login_page import LoginPage
from pages.register_page import RegisterPage

TEST_ID = "T011"
TEST_PASSWORD = "S3cure!Pass2026"
NEW_PASSWORD = "NewPass!2026"


def _register_and_stay_logged_in(driver: WebDriver, base_url: str) -> str:
    """
    Register a unique account; OpenCart logs the new customer in automatically.
    """
    email = f"t011.{uuid.uuid4().hex[:8]}@example.com"
    RegisterPage(driver, base_url).open().register(
        "Truong", "Tester", email, "+61400000000", TEST_PASSWORD
    )
    return email


def test_scenario_1_successful_password_change(
    driver: WebDriver,
    base_url: str,
    snap: Callable[[str], Path],
) -> None:
    email = _register_and_stay_logged_in(driver, base_url)

    change = ChangePasswordPage(driver, base_url).open()
    assert change.is_loaded(), "the Change Password page should be displayed"

    change.change(NEW_PASSWORD)
    message: str = change.success_text()  # waits for the confirmation banner
    snap("t011_scenario_1")

    assert "account/account" in driver.current_url, "should be redirected to My Account"
    assert "password has been successfully updated" in message.lower(), (
        f"expected password-updated confirmation, got: {message!r}"
    )

    # The new password must now grant access.
    BasePage(driver, base_url).logout()
    LoginPage(driver, base_url).open().login(email, NEW_PASSWORD)
    assert AccountPage(driver, base_url).is_loaded(), "login with the new password should succeed"
    snap("t011_scenario_1_relogin")


def test_scenario_2_passwords_do_not_match_rejected(
    driver: WebDriver,
    base_url: str,
    snap: Callable[[str], Path],
) -> None:
    _register_and_stay_logged_in(driver, base_url)

    change = ChangePasswordPage(driver, base_url).open()
    assert change.is_loaded(), "the Change Password page should be displayed"

    change.change(NEW_PASSWORD, password_confirm="Different!123")
    errors: list[str] = change.wait_for_field_errors()
    snap("t011_scenario_2")

    assert "Password confirmation does not match password!" in errors, (
        f"expected mismatch error, got: {errors!r}"
    )
    assert "account/password" in driver.current_url, "should stay on the Change Password page"


def test_scenario_3_password_below_minimum_length_rejected(
    driver: WebDriver,
    base_url: str,
    snap: Callable[[str], Path],
) -> None:
    _register_and_stay_logged_in(driver, base_url)

    change = ChangePasswordPage(driver, base_url).open()
    assert change.is_loaded(), "the Change Password page should be displayed"

    change.change("abc")  # 3 characters: one below the 4-character minimum
    errors: list[str] = change.wait_for_field_errors()
    snap("t011_scenario_3")

    assert "Password must be between 4 and 20 characters!" in errors, (
        f"expected length error, got: {errors!r}"
    )
    assert "account/password" in driver.current_url, "should stay on the Change Password page"
