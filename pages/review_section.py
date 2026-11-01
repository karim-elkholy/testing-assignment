"""
Author: Monark

Reviews tab on the product page (F13):
https://opencart.abstracta.us/index.php?route=product/product&product_id=40
"""

from typing import Self

from selenium.webdriver.common.by import By

from pages.base_page import BasePage, Locator
from pages.product_page import IPHONE_PRODUCT_ID


class ReviewSection(BasePage):
    REVIEWS_TAB: Locator = (By.CSS_SELECTOR, "a[href='#tab-review']")
    NAME_INPUT: Locator = (By.ID, "input-name")
    REVIEW_TEXTAREA: Locator = (By.ID, "input-review")
    SUBMIT_BUTTON: Locator = (By.ID, "button-review")
    # Stock OpenCart injects the result as an .alert above the form (AJAX),
    # green for success and red for validation warnings.
    MESSAGE: Locator = (By.CSS_SELECTOR, "#form-review .alert, #tab-review .alert")

    def open(self, route: str = f"product/product&product_id={IPHONE_PRODUCT_ID}") -> Self:
        super().open(route)
        return self

    def open_reviews_tab(self) -> Self:
        self.click(self.REVIEWS_TAB)
        self.find(self.NAME_INPUT)
        return self

    @staticmethod
    def _rating(stars: int) -> Locator:
        return (By.CSS_SELECTOR, f"input[name='rating'][value='{stars}']")

    def fill(self, name: str, text: str, rating: int | None) -> Self:
        """
        Fill the review form. `rating` is 1-5, or None to leave no star chosen.
        """
        self.type(self.NAME_INPUT, name)
        self.type(self.REVIEW_TEXTAREA, text)
        if rating is not None:
            self.click(self._rating(rating))
        return self

    def submit(self) -> Self:
        self.click(self.SUBMIT_BUTTON)
        self.find(self.MESSAGE)
        return self

    def message(self) -> str:
        """
        Text of the success/warning alert shown after submitting.
        """
        texts = [m.text for m in self.find_all(self.MESSAGE) if m.is_displayed() and m.text.strip()]
        return "\n".join(texts).strip()
