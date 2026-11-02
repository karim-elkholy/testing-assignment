"""
Author: Alexander Paceskoski

Product detail page, e.g. iPhone: route=product/product&product_id=40
"""

from typing import Self

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec

from pages.base_page import BasePage, Locator

# The iPhone used by the cart tests (product 40 on the old LambdaTest
# playground and on the current demo alike).
IPHONE_PRODUCT_ID: int = 40
# A second Apple product with its own price, model and availability, used
# for the side-by-side comparison scenarios (F8).
MACBOOK_PRODUCT_ID: int = 43


class ProductPage(BasePage):
    ADD_TO_CART: Locator = (By.ID, "button-cart")
    # Stock OpenCart confirms actions with a banner above the content.
    SUCCESS_BANNER: Locator = (By.CSS_SELECTOR, ".alert-success")

    def __init__(self, driver: WebDriver, base_url: str, product_id: int = IPHONE_PRODUCT_ID) -> None:
        super().__init__(driver, base_url)
        self.product_id: int = product_id

    def open(self, route: str | None = None) -> Self:
        super().open(route or f"product/product&product_id={self.product_id}")
        return self

    def add_to_cart(self) -> Self:
        self.click(self.ADD_TO_CART)
        self.wait.until(ec.visibility_of_element_located(self.SUCCESS_BANNER))
        return self

    def toast_text(self) -> str:
        """
        Text of the add-to-cart success banner, e.g.
        'Success: You have added iPhone to your shopping cart!'.
        """
        texts = [t.text for t in self.driver.find_elements(*self.SUCCESS_BANNER) if t.text.strip()]
        return "\n".join(texts).strip()

    # --- wish list and comparison (F7 / F8) ---------------------------------

    def add_to_wishlist(self) -> Self:
        """
        Click this product's heart button and wait for the response banner.
        Logged in it confirms the product was saved; as a guest the same
        banner is the 'must login or create an account' prompt.
        """
        self.click(self._product_action_button("wishlist.add"))
        self.wait.until(ec.visibility_of_element_located(self.SUCCESS_BANNER))
        return self

    def compare_this_product(self) -> Self:
        """
        Click 'Compare this Product' and wait for the confirmation banner.
        """
        self.click(self._product_action_button("compare.add"))
        self.wait.until(ec.visibility_of_element_located(self.SUCCESS_BANNER))
        return self

    def _product_action_button(self, js_call: str) -> Locator:
        """
        Locator for this product's wish-list/compare button. Related-product
        tiles further down the page carry buttons of their own for other
        product ids, so match the id baked into the button's onclick.
        """
        return (
            By.CSS_SELECTOR,
            f"button[onclick*=\"{js_call}('{self.product_id}')\"]",
        )
