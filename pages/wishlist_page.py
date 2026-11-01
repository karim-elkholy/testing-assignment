"""
Author: Daniel

Wish List page: https://opencart.abstracta.us/index.php?route=account/wishlist

Also holds the product-page action that saves a product to the wish list,
so every wish-list interaction used by T007 lives in one Page Object.
"""

from typing import Self

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from pages.base_page import BasePage, Locator

WISHLIST_ROUTE: str = "account/wishlist"


class WishListPage(BasePage):
    # Header link, e.g. title="Wish List (1)". The title attribute is updated by
    # the site's AJAX call, so it is a reliable place to read the counter.
    HEADER_TOTAL: Locator = (By.ID, "wishlist-total")
    # Product-name links in the wish list table (one per saved product).
    PRODUCT_NAMES: Locator = (By.CSS_SELECTOR, "#content table tbody td.text-left a")
    # The site shows add/remove feedback as a dismissible banner.
    ALERT: Locator = (By.CSS_SELECTOR, ".alert-dismissible")

    def open(self, route: str = WISHLIST_ROUTE) -> Self:
        super().open(route)
        return self

    # --- product page action -------------------------------------------------

    def add_from_product_page(self, product_id: int) -> str:
        """
        Open the product page and click its heart ('Add to Wish List') button.

        Returns the feedback banner text, e.g.
        'Success: You have added iPhone to your wish list!'.
        """
        super().open(f"product/product&product_id={product_id}")
        # Remove any old banner first so the wait below can only match the
        # banner produced by THIS click (the site adds it via AJAX).
        self.driver.execute_script("document.querySelectorAll('.alert').forEach(a => a.remove())")
        # Select the button by its onclick handler: it is unique per product and,
        # unlike the title attribute, is not rewritten by Bootstrap tooltips.
        self.click((By.CSS_SELECTOR, f"#content button[onclick=\"wishlist.add('{product_id}');\"]"))
        return self.find(self.ALERT).text.replace("×", "").strip()

    # --- wish list page ------------------------------------------------------

    def header_total(self) -> str:
        """
        Header counter text, e.g. 'Wish List (1)'.
        """
        return self.find(self.HEADER_TOTAL).get_attribute("title") or ""

    def product_names(self) -> list[str]:
        """
        Names of all products currently listed in the wish list table.
        """
        return [a.text.strip() for a in self.find_all(self.PRODUCT_NAMES) if a.text.strip()]

    def remove(self, product_id: int) -> str:
        """
        Click the red 'Remove' (X) button of one product and return the banner text.
        """
        self.click((By.CSS_SELECTOR, f'#content a.btn-danger[href*="remove={product_id}"]'))
        # Removing reloads the page; wait until the product's row is gone.
        self.wait.until(ec.invisibility_of_element_located(
            (By.CSS_SELECTOR, f'#content a.btn-danger[href*="remove={product_id}"]')
        ))
        return self.find(self.ALERT).text.replace("×", "").strip()
