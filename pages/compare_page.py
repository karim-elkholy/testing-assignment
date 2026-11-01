"""
Author: Daniel

Product Comparison page: https://opencart.abstracta.us/index.php?route=product/compare

Also holds the 'Compare this Product' actions on product and category pages,
so every comparison interaction used by T008 lives in one Page Object.
"""

from typing import Self

from selenium.common.exceptions import ElementClickInterceptedException
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

    def _click_compare_and_wait(self, button_css: str, product_id: int) -> str:
        """
        Click a 'Compare this Product' button and return the banner text.
        """
        # Clear old banners so we only ever read the one for this click.
        self.driver.execute_script("document.querySelectorAll('.alert').forEach(a => a.remove())")
        button = self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, button_css)))
        # Centre the button first: at the window edge a neighbouring product tile can
        # cover it and the click is rejected as 'intercepted'.
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        try:
            self.wait.until(ec.element_to_be_clickable(button)).click()
        except ElementClickInterceptedException:
            # The page layout moved under the pointer; use the button's own click handler.
            self.driver.execute_script("arguments[0].click();", button)
        # The site fades banners out a few seconds after ANY button click, so a faded
        # banner counts as 'not visible' to Selenium. Wait for the banner to exist in
        # the page (not to be visible) and read its raw text.
        banner = self.wait.until(lambda d: d.find_elements(*self.ALERT))[0]
        text: str = (banner.get_attribute("textContent") or "").replace("\u00d7", "").strip()
        # After every add the site scrolls the page to the top (a ~0.6s jQuery animation).
        # Wait for it to finish, otherwise the next click lands on a moving page.
        self.wait.until(lambda d: d.execute_script(
            "return !(window.jQuery && jQuery('html, body').is(':animated'));"
        ))
        # Wait until the server has stored the product in the comparison list, so the
        # next page load cannot read a stale list.
        self.wait.until(lambda d: d.execute_script(
            "const x = new XMLHttpRequest();"
            "x.open('GET', 'index.php?route=product/compare', false); x.send();"
            "return x.responseText.includes('remove=' + arguments[0]);",
            product_id,
        ))
        return text

    def add_from_product_page(self, product_id: int) -> str:
        """
        Open a product page and click its 'Compare this Product' button.
        """
        super().open(f"product/product&product_id={product_id}")
        return self._click_compare_and_wait(
            f"#content button[onclick=\"compare.add('{product_id}');\"]", product_id
        )

    def add_from_category_page(self, product_id: int) -> str:
        """
        Click 'Compare this Product' on a product tile of the category page
        that is already open (e.g. Desktops).
        """
        return self._click_compare_and_wait(
            f".product-thumb button[onclick=\"compare.add('{product_id}');\"]", product_id
        )

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
        return alerts[0].text.replace("\u00d7", "").strip() if alerts else ""

    def has_table(self) -> bool:
        return len(self.find_all(self.TABLE)) > 0

    def content_text(self) -> str:
        return self.find(self.CONTENT).text.strip()
