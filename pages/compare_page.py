"""
Author: Karim Elkholy

Product Comparison page (F8):
https://opencart.abstracta.us/index.php?route=product/compare

The comparison table has one labelled row per detail ('Product', 'Image',
'Price', 'Model', 'Brands', 'Availability', ...) and one column per
compared product.
"""

from typing import Self

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from pages.base_page import BasePage, Locator


class ComparePage(BasePage):
    # One row per detail; the first row is the product names.
    TABLE_ROW: Locator = (By.CSS_SELECTOR, "#content table tbody tr")
    # Per product column, at the bottom of the table.
    REMOVE_LINK: Locator = (By.CSS_SELECTOR, "#content table a.btn-danger")
    # Stock OpenCart confirms actions with a green banner above the content.
    SUCCESS_BANNER: Locator = (By.CSS_SELECTOR, ".alert-success")

    def open(self, route: str = "product/compare") -> Self:
        super().open(route)
        return self

    def product_names(self) -> list[str]:
        """
        Names of the compared products, in column order, e.g.
        ['iPhone', 'MacBook']. Empty once the comparison is cleared.
        """
        rows = self.driver.find_elements(*self.TABLE_ROW)
        if not rows:
            return []
        cells = rows[0].find_elements(By.CSS_SELECTOR, "th,td")
        # The first cell is the row label ('Product'); the rest are columns.
        return [cell.text.strip() for cell in cells[1:]]

    def row_values(self, label: str) -> list[str]:
        """
        Values of a labelled detail row across the product columns, e.g.
        row_values('Price') -> ['$123.20', '$602.00'].
        """
        for row in self.driver.find_elements(*self.TABLE_ROW):
            cells = row.find_elements(By.CSS_SELECTOR, "th,td")
            if cells and cells[0].text.strip() == label:
                return [cell.text.strip() for cell in cells[1:]]
        return []

    def remove(self, name: str) -> Self:
        """
        Click the remove link in a product's column and wait until that
        product is no longer listed.
        """
        last_error: TimeoutException | None = None
        for _ in range(2):
            names = self.product_names()
            if name not in names:
                return self
            self.driver.find_elements(*self.REMOVE_LINK)[names.index(name)].click()
            # Removing navigates; mid-reload the DOM briefly has no table
            # at all, so settle on the new page before callers read again.
            try:
                self.wait.until(lambda d: name not in self.product_names())
                self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
                return self
            except TimeoutException as exc:
                # The shared demo occasionally drops a remove on its loaded
                # backends even after the confirmation banner; click again.
                last_error = exc
        assert last_error is not None
        raise last_error

    def success_text(self) -> str:
        """
        Text of the green response banner, e.g. 'Success: You have modified
        your product comparison!'.
        """
        self.wait.until(ec.visibility_of_element_located(self.SUCCESS_BANNER))
        texts = [t.text for t in self.driver.find_elements(*self.SUCCESS_BANNER) if t.text.strip()]
        return "\n".join(texts).strip()
