"""
Author: An Truong Le

Edit Account (My Account Information) page: https://opencart.abstracta.us/index.php?route=account/edit
"""

from typing import Self

from selenium.webdriver.common.by import By

from pages.base_page import BasePage, Locator


class EditAccountPage(BasePage):
    FIRST_NAME: Locator = (By.ID, "input-firstname")
    LAST_NAME: Locator = (By.ID, "input-lastname")
    EMAIL: Locator = (By.ID, "input-email")
    TELEPHONE: Locator = (By.ID, "input-telephone")
    CONTINUE: Locator = (By.CSS_SELECTOR, "input[type=submit][value=Continue]")
    # Rejected updates show an .alert-danger banner (e.g. duplicate email)
    # and/or per-field .text-danger errors; accepted ones redirect to
    # My Account with an .alert-success banner.
    ALERT: Locator = (By.CSS_SELECTOR, ".alert-danger")
    SUCCESS: Locator = (By.CSS_SELECTOR, ".alert-success")
    FIELD_ERRORS: Locator = (By.CSS_SELECTOR, ".text-danger")
    HEADING_TEXT: str = "My Account Information"

    def open(self, route: str = "account/edit") -> Self:
        super().open(route)
        return self

    def is_loaded(self) -> bool:
        """
        True once the pre-filled account form is visible (requires a logged-in user).
        """
        self.find(self.FIRST_NAME)
        return "account/edit" in self.driver.current_url and self.contains_text(self.HEADING_TEXT)

    def value(self, locator: Locator) -> str:
        """
        Current value of a form field.
        """
        return self.find(locator).get_attribute("value") or ""

    def update(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        telephone: str | None = None,
    ) -> Self:
        """
        Change only the given fields ("" clears a field), then click Continue.
        """
        values: list[tuple[Locator, str | None]] = [
            (self.FIRST_NAME, first_name),
            (self.LAST_NAME, last_name),
            (self.EMAIL, email),
            (self.TELEPHONE, telephone),
        ]
        for locator, new_value in values:
            if new_value is None:
                continue
            field = self.find(locator)
            field.clear()
            if new_value:
                field.send_keys(new_value)
        self.click(self.CONTINUE)
        return self

    def warning_text(self) -> str:
        return self.find(self.ALERT).text.strip()

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
