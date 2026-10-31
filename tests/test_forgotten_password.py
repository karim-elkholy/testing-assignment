"""
Author: An Truong Le
Tester: An Truong Le

T010 - Forgotten Password (F10) - all 3 scenarios.

Function IDs/Names: F10 Forgotten Password
(https://opencart.abstracta.us/index.php?route=account/forgotten)

Scenario 1: a reset request for a registered email is accepted.
Scenario 2: a reset request for an unregistered email is rejected.
Scenario 3: a reset request with the email field left empty is rejected.

Scenario 1 uses the account registered once per session by the
`registered_user` fixture (registration before password reset, F2 -> F10).
Drafted with AI assistance (Claude) and reviewed by the author.
"""
import uuid
from collections.abc import Callable
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver

from pages.forgotten_password_page import ForgottenPasswordPage
from pages.login_page import LoginPage

TEST_ID = "T010"
NOT_FOUND_WARNING = "The E-Mail Address was not found in our records"


def test_scenario_1_registered_email_reset_accepted(
    driver: WebDriver,
    base_url: str,
    snap: Callable[[str], Path],
    registered_user: dict[str, str],
) -> None:
    # Reach the form the way a user would: via the link on the login page.
    login = LoginPage(driver, base_url).open()
    login.click(login.FORGOTTEN_LINK)

    forgotten = ForgottenPasswordPage(driver, base_url)
    assert forgotten.is_loaded(), "the 'Forgot Your Password?' page should be displayed"

    forgotten.request_reset(registered_user["email"])
    message: str = forgotten.success_text()  # waits for the confirmation banner
    snap("t010_scenario_1")

    assert "account/login" in driver.current_url, "should be redirected to the login page"
    assert "email" in message.lower(), f"expected a reset-email confirmation, got: {message!r}"


def test_scenario_2_unregistered_email_rejected(
    driver: WebDriver,
    base_url: str,
    snap: Callable[[str], Path],
) -> None:
    ghost_email = f"ghost.{uuid.uuid4().hex[:8]}@example.com"

    forgotten = ForgottenPasswordPage(driver, base_url).open()
    assert forgotten.is_loaded(), "the 'Forgot Your Password?' page should be displayed"

    forgotten.request_reset(ghost_email)
    warning: str = forgotten.warning_text()  # waits for the warning banner
    snap("t010_scenario_2")

    assert NOT_FOUND_WARNING in warning, f"expected 'not found' warning, got: {warning!r}"
    assert "account/forgotten" in driver.current_url, "should stay on the Forgotten Password page"


def test_scenario_3_empty_email_rejected(
    driver: WebDriver,
    base_url: str,
    snap: Callable[[str], Path],
) -> None:
    forgotten = ForgottenPasswordPage(driver, base_url).open()
    assert forgotten.is_loaded(), "the 'Forgot Your Password?' page should be displayed"

    forgotten.request_reset("")  # field left empty
    warning: str = forgotten.warning_text()
    snap("t010_scenario_3")

    assert NOT_FOUND_WARNING in warning, f"expected 'not found' warning, got: {warning!r}"
    assert "account/forgotten" in driver.current_url, "should stay on the Forgotten Password page"
