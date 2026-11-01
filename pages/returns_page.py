"""
Author: Daniel

Product Returns form: https://opencart.abstracta.us/index.php?route=account/return/add
"""

from typing import ClassVar, Self

from selenium.webdriver.common.by import By

from pages.base_page import BasePage, Locator

SUCCESS_MESSAGE: str = "Thank you for submitting your return request."


class ReturnsPage(BasePage):
    # Text fields of the RMA form, keyed by the name used in the tests.
    FIELDS: ClassVar[dict[str, Locator]] = {
        "firstname": (By.ID, "input-firstname"),
        "lastname": (By.ID, "input-lastname"),
        "email": (By.ID, "input-email"),
        "telephone": (By.ID, "input-telephone"),
        "order_id": (By.ID, "input-order-id"),
        "date_ordered": (By.ID, "input-date-ordered"),
        "product": (By.ID, "input-product"),
        "model": (By.ID, "input-model"),
        "quantity": (By.ID, "input-quantity"),
        "comment": (By.ID, "input-comment"),
    }
    SUBMIT: Locator = (By.CSS_SELECTOR, "#content input[type=submit][value=Submit]")
    # Each invalid field gets a red .text-danger message inside its form group.
    FIELD_ERRORS: Locator = (By.CSS_SELECTOR, "#content .text-danger")
    CONTENT: Locator = (By.ID, "content")

    def open(self, route: str = "account/return/add") -> Self:
        super().open(route)
        return self

    def fill(self, data: dict[str, str], reason: str | None = None) -> Self:
        """
        Type each value into its field and tick the return reason radio.

        `reason` is the visible label, e.g. 'Dead On Arrival'; None leaves all
        reasons unticked (used by the empty-form scenario).
        """
        for name, value in data.items():
            self.type(self.FIELDS[name], value)
        if reason is not None:
            # Radios are wrapped in their <label>, so match on the label text.
            self.click((By.XPATH, f"//label[normalize-space()='{reason}']/input[@name='return_reason_id']"))
        return self

    def submit(self) -> Self:
        self.click(self.SUBMIT)
        # Either the success page loads or the form re-renders with errors.
        self.wait.until(
            lambda d: "account/return/success" in d.current_url or self.find_all(self.FIELD_ERRORS)
        )
        return self

    def errors(self) -> dict[str, str]:
        """
        Field name -> error text, e.g. {'telephone': 'Telephone must be between 3 and 32 characters!'}.
        """
        result: dict[str, str] = {}
        for err in self.find_all(self.FIELD_ERRORS):
            group = err.find_element(By.XPATH, "./ancestor::div[contains(@class,'form-group')][1]")
            field = group.find_elements(By.CSS_SELECTOR, "input, textarea")
            if field:
                result[field[0].get_attribute("name")] = err.text.strip()
        return result

    def content_text(self) -> str:
        return self.find(self.CONTENT).text.strip()
