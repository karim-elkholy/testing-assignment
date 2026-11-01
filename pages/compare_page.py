"""
Author: Daniel

Product Comparison page: https://opencart.abstracta.us/index.php?route=product/compare

Also holds the 'Compare this Product' actions on product and category pages,
so every comparison interaction used by T008 lives in one Page Object.
"""

from typing import Self

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from pages.base_page import BasePage, Locator

COMPARE_ROUTE: str = "product/compare"


class ComparePage(BasePage):
    # Product names in the comparison table header row (bold links).
    PRODUCT_NAMES: Locator = (By.CSS_SELECTOR, "#content table a strong")
    # The comparison table itself; absent when nothing is being compared.
    TABLE: Locator = (By.CSS_SELECTOR, "#content table.table")
    # 'Continue' button shown on the empty comparison page.
    CONTINUE: Locator = (By.CSS_SELECTOR, "#content a.btn-primary")
    CONTENT: Locator = (By.ID, "content")
    ALERT: Locator = (By.CSS_SELECTOR, ".alert-success")
    # Category-page link 'Product Compare (n)' - counts products being compared.
    HEADER_COUNTER: Locator = (By.ID, "compare-total")

    def open(self, route: str = COMPARE_ROUTE) -> Self:
        super().open(route)
        return self

    # --- add actions -----------------------------------------------------------

    def _click_compare_and_wait(self, button_css: str) -> str:
        """
        Click a 'Compare this Product' button and return the banner text.
        """
        # Clear old banners so we only ever read the one for this click.
        self.driver.execute_script("document.querySelectorAll('.alert').forEach(a => a.remove())")
        self.click((By.CSS_SELECTOR, button_css))
        # The site fades banners out a few seconds after ANY button click, so a timer
        # from an earlier click can start fading this new banner while it is still
        # appearing. A faded banner counts as 'not visible' to Selenium, so wait for
        # the banner to exist in the page (not to be visible) and read its raw text.
        banner = self.wait.until(lambda d: d.find_elements(*self.ALERT))[0]
        return (banner.get_attribute("textContent") or "").replace("×", "").strip()

    def add_from_product_page(self, product_id: int) -> str:
        """
        Open a product page and click its 'Compare this Product' button.
        """
        super().open(f"product/product&product_id={product_id}")
        return self._click_compare_and_wait(f"#content button[onclick=\"compare.add('{product_id}');\"]")

    def add_from_category_page(self, product_id: int) -> str:
        """
        Click 'Compare this Product' on a product tile of the category page
        that is already open (e.g. Desktops).
        """
        return self._click_compare_and_wait(f".product-thumb button[onclick=\"compare.add('{product_id}');\"]")

    def header_counter(self) -> str:
        """
        Counter text on the category page, e.g. 'Product Compare (4)'.
        """
        return self.find(self.HEADER_COUNTER).text.strip()

    # --- comparison page -----------------------------------------------------

    def product_names(self) -> list[str]:
        """
        Names of the compared products, in column order (left to right).
        """
        return [el.text.strip() for el in self.find_all(self.PRODUCT_NAMES) if el.text.strip()]

    def row_values(self, label: str) -> list[str]:
        """
        Values of one attribute row, e.g. row_values('Price') -> ['$123.20', '$602.00'].
        """
        for row in self.find_all((By.CSS_SELECTOR, "#content table tr")):
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells and cells[0].text.strip() == label:
                return [c.text.strip() for c in cells[1:]]
        return []

    def remove(self, product_id: int) -> str:
        """
        Click the red 'Remove' button under one product and return the banner text.
        """
        self.click((By.CSS_SELECTOR, f'#content a.btn-danger[href*="remove={product_id}"]'))
        # Removing reloads the page; wait until that product's Remove button is gone.
        self.wait.until(ec.invisibility_of_element_located(
            (By.CSS_SELECTOR, f'#content a.btn-danger[href*="remove={product_id}"]')
        ))
        alerts = self.find_all(self.ALERT)
        return alerts[0].text.replace("×", "").strip() if alerts else ""

    def has_table(self) -> bool:
        return len(self.find_all(self.TABLE)) > 0

    def content_text(self) -> str:
        return self.find(self.CONTENT).text.strip()
