"""
Author: An Truong Le

Change Password page: https://opencart.abstracta.us/index.php?route=account/password
"""

from typing import Self

from selenium.webdriver.common.by import By

from pages.base_page import BasePage, Locator


class ChangePasswordPage(BasePage):
    PASSWORD: Locator = (By.ID, "input-password")
    PASSWORD_CONFIRM: Locator = (By.ID, "input-confirm")
    CONTINUE: Locator = (By.CSS_SELECTOR, "input[type=submit][value=Continue]")
    FIELD_ERRORS: Locator = (By.CSS_SELECTOR, ".text-danger")
    # An accepted change redirects to My Account with an .alert-success banner.
    SUCCESS: Locator = (By.CSS_SELECTOR, ".alert-success")
    HEADING_TEXT: str = "Change Password"

    def open(self, route: str = "account/password") -> Self:
        super().open(route)
        return self

    def is_loaded(self) -> bool:
        """
        True once the Change Password form is visible (requires a logged-in user).
        """
        self.find(self.PASSWORD)
        return "account/password" in self.driver.current_url and self.contains_text(self.HEADING_TEXT)

    def change(self, password: str, password_confirm: str | None = None) -> Self:
        """
        Fill both password fields and click Continue (no success waiting).
        """
        if password_confirm is None:
            password_confirm = password
        self.type(self.PASSWORD, password)
        self.type(self.PASSWORD_CONFIRM, password_confirm)
        self.click(self.CONTINUE)
        return self

    def success_text(self) -> str:
        return self.find(self.SUCCESS).text.strip()

    def field_errors(self) -> list[str]:
        return [el.text.strip() for el in self.find_all(self.FIELD_ERRORS) if el.text.strip()]

    def wait_for_field_errors(self) -> list[str]:
        """
        Wait for the per-field validation errors to render, then return them.
        """
        self.wait.until(lambda d: self.field_errors())
        return self.field_errors()
