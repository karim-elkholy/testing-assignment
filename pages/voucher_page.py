"""
Author: Daniel

Purchase a Gift Certificate form: https://opencart.abstracta.us/index.php?route=account/voucher
"""

from typing import Self

from selenium.webdriver.common.by import By

from pages.base_page import BasePage, Locator

SUCCESS_MESSAGE: str = "Thank you for purchasing a gift certificate!"
AMOUNT_ERROR: str = "Amount must be between $1.00 and $1,000.00!"


class VoucherPage(BasePage):
    TO_NAME: Locator = (By.ID, "input-to-name")
    TO_EMAIL: Locator = (By.ID, "input-to-email")
    FROM_NAME: Locator = (By.ID, "input-from-name")
    FROM_EMAIL: Locator = (By.ID, "input-from-email")
    MESSAGE: Locator = (By.ID, "input-message")
    AMOUNT: Locator = (By.ID, "input-amount")
    AGREE: Locator = (By.CSS_SELECTOR, "#content input[name=agree]")
    CONTINUE: Locator = (By.CSS_SELECTOR, "#content input[type=submit][value=Continue]")
    FIELD_ERRORS: Locator = (By.CSS_SELECTOR, "#content .text-danger")
    # The 'non-refundable' warning shows as a red banner above the form.
    WARNING: Locator = (By.CSS_SELECTOR, ".alert-danger")
    CONTENT: Locator = (By.ID, "content")

    def open(self, route: str = "account/voucher") -> Self:
        super().open(route)
        return self

    def fill(self, to_name: str, to_email: str, from_name: str, from_email: str,
             theme: str | None, message: str, amount: str, agree: bool) -> Self:
        """
        Fill the whole form. `theme` is the radio label ('Birthday', 'Christmas',
        'General') or None to leave it unselected; `agree` ticks the
        non-refundable checkbox.
        """
        self.type(self.TO_NAME, to_name)
        self.type(self.TO_EMAIL, to_email)
        self.type(self.FROM_NAME, from_name)
        self.type(self.FROM_EMAIL, from_email)
        if theme is not None:
            self.click((By.XPATH, f"//label[normalize-space()='{theme}']/input[@name='voucher_theme_id']"))
        self.type(self.MESSAGE, message)
        self.type(self.AMOUNT, amount)
        checkbox = self.find(self.AGREE)
        if checkbox.is_selected() != agree:  # only click when the state must change
            checkbox.click()
        return self

    def submit(self) -> Self:
        self.click(self.CONTINUE)
        # Either the success page loads or the form re-renders with errors.
        self.wait.until(
            lambda d: "account/voucher/success" in d.current_url
            or self.find_all(self.FIELD_ERRORS)
            or self.find_all(self.WARNING)
        )
        return self

    def errors(self) -> list[str]:
        """All red field-level error messages currently shown."""
        return [e.text.strip() for e in self.find_all(self.FIELD_ERRORS) if e.text.strip()]

    def warning_text(self) -> str:
        banners = self.find_all(self.WARNING)
        return banners[0].text.replace("×", "").strip() if banners else ""

    def content_text(self) -> str:
        return self.find(self.CONTENT).text.strip()
