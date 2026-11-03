"""
Author: Alexander Paceskoski

Category page with product sorting: route=product/category&path=20 (Desktops).
"""

import re
from typing import Self

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage, Locator

# The Desktops category holds 12 varied products - ideal for sorting checks.
# (Sorting used to run on Cameras on the previous playground, but that
# category holds only 2 products on the current demo.)
DESKTOPS_ROUTE = "product/category&path=20"


class CategoryPage(BasePage):
    SORT_DROPDOWN: Locator = (By.ID, "input-sort")
    PRODUCT_TITLES: Locator = (By.CSS_SELECTOR, ".product-thumb h4 a")
    PRODUCT_PRICES: Locator = (By.CSS_SELECTOR, ".product-thumb .price")
    # 'Product Compare (n)' link above the tiles, e.g. on Desktops.
    COMPARE_COUNTER: Locator = (By.ID, "compare-total")
    # Stock OpenCart confirms actions with a green banner above the content.
    SUCCESS_BANNER: Locator = (By.CSS_SELECTOR, ".alert-success")

    def open(self, route: str = DESKTOPS_ROUTE) -> Self:
        super().open(route)
        return self

    def sort_by(self, option_text: str) -> Self:
        """
        Pick an option in the Sort By dropdown and wait for the reload.
        """
        select = Select(self.find(self.SORT_DROPDOWN))
        select.select_by_visible_text(option_text)
        self.wait.until(lambda d: "sort=" in d.current_url)
        self.wait.until(ec.element_to_be_clickable(self.SORT_DROPDOWN))
        return self

    def titles(self) -> list[str]:
        return [el.text.strip() for el in self.find_all(self.PRODUCT_TITLES) if el.text.strip()]

    def prices(self) -> list[float]:
        """
        The displayed price of each product, e.g. 146.0 for '$146.00'.

        Products on special render the current price first (price-new) and
        the struck-through old price after it, so the first match is the
        price OpenCart sorts by.
        """
        prices: list[float] = []
        for el in self.find_all(self.PRODUCT_PRICES):
            match = re.search(r"\$([\d,.]+)", el.text)
            if match:
                prices.append(float(match.group(1).replace(",", "")))
        return prices

    # --- product comparison (F8) --------------------------------------------

    def compare_count(self) -> int:
        """
        Number in the 'Product Compare (n)' link above the tiles.
        """
        match = re.search(r"\((\d+)\)", self.find(self.COMPARE_COUNTER).text)
        return int(match.group(1)) if match else 0

    def compare_tile(self, product_id: int, expected_count: int) -> Self:
        """
        Click a product tile's 'Compare this Product' button and wait until
        the counter shows `expected_count`.

        The counter only moves once the add has been processed, so this
        also guarantees the request finished before callers navigate away.
        The previous add's banner is closed first: it overlays the tiles
        and intercepts the next click. The shared demo also occasionally
        drops a compare add, hence the re-click while the counter
        disagrees.
        """
        last_error: Exception | None = None
        for _ in range(3):
            self._dismiss_banner()
            try:
                self.click(self._tile_compare_button(product_id))
                self.wait.until(lambda d: self.compare_count() == expected_count)
                return self
            except (ElementClickInterceptedException, TimeoutException) as exc:
                last_error = exc
        assert last_error is not None
        raise last_error

    def click_compare_tile(self, product_id: int, product_name: str) -> None:
        """
        Click a tile's compare button once and wait for that product's own
        confirmation, so the add request finishes before callers navigate
        away. At the four-product limit the counter cannot confirm an add
        (a dropped add also leaves it unchanged), so callers verify the
        effect on the compare page and call this again to retry.
        """
        self._dismiss_banner()
        try:
            self.click(self._tile_compare_button(product_id))
        except ElementClickInterceptedException:
            # The banner reappeared between the dismiss and the click.
            self._dismiss_banner()
            self.click(self._tile_compare_button(product_id))
        try:
            self.wait.until(
                lambda d: any(
                    product_name in el.text
                    for el in self.driver.find_elements(*self.SUCCESS_BANNER)
                )
            )
        except TimeoutException:
            pass  # e.g. the product was already in the comparison; callers verify

    def _dismiss_banner(self) -> None:
        """
        Close the response banner via its × button so it cannot cover the
        product tiles (OpenCart parks each banner above the content).
        """
        for close in self.driver.find_elements(By.CSS_SELECTOR, ".alert-dismissible .close"):
            try:
                close.click()
            except (ElementClickInterceptedException, StaleElementReferenceException):
                # Fall back to removing it if the button will not take the click.
                self.driver.execute_script(
                    "document.querySelectorAll('.alert-dismissible').forEach(a => a.remove())"
                )
                return

    def _tile_compare_button(self, product_id: int) -> Locator:
        # Every tile carries its own compare button for its product id, so
        # match the id baked into the button's onclick.
        return (By.CSS_SELECTOR, f"button[onclick*=\"compare.add('{product_id}')\"]")
