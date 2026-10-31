"""
Author: An Truong Le

Forgotten Password page: https://opencart.abstracta.us/index.php?route=account/forgotten
"""

from typing import Self

from selenium.webdriver.common.by import By

from pages.base_page import BasePage, Locator


class ForgottenPasswordPage(BasePage):
    EMAIL: Locator = (By.ID, "input-email")
    CONTINUE: Locator = (By.CSS_SELECTOR, "input[type=submit][value=Continue]")
    # A rejected request renders an .alert-danger banner on this page; an
    # accepted one redirects to the login page with an .alert-success banner.
    ALERT: Locator = (By.CSS_SELECTOR, ".alert-danger")
    SUCCESS: Locator = (By.CSS_SELECTOR, ".alert-success")
    HEADING_TEXT: str = "Forgot Your Password?"

    def open(self, route: str = "account/forgotten") -> Self:
        super().open(route)
        return self

    def is_loaded(self) -> bool:
        """
        True once the 'Forgot Your Password?' form is visible.
        """
        self.find(self.EMAIL)
        return "account/forgotten" in self.driver.current_url and self.contains_text(self.HEADING_TEXT)

    def request_reset(self, email: str) -> Self:
        """
        Enter `email` (empty string leaves the field blank) and click Continue.
        """
        field = self.find(self.EMAIL)
        field.clear()
        if email:
            field.send_keys(email)
        self.click(self.CONTINUE)
        return self

    def warning_text(self) -> str:
        """
        Text of the warning banner shown after a rejected request.
        """
        return self.find(self.ALERT).text.strip()

    def success_text(self) -> str:
        """
        Text of the confirmation banner shown after an accepted request.
        """
        return self.find(self.SUCCESS).text.strip()
