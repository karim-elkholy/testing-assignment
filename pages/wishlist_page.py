"""
Author: Karim Elkholy

My Wish List page (F7):
https://opencart.abstracta.us/index.php?route=account/wishlist
"""

from typing import Self

from selenium.webdriver.common.by import By

from pages.base_page import BasePage, Locator


class WishlistPage(BasePage):
    # One row per saved product: image, name, model, availability, price,
    # actions. When the list is empty there is no table at all.
    TABLE_ROW: Locator = (By.CSS_SELECTOR, "#content table tbody tr")
    # Per row, at the end of the row.
    REMOVE_LINK: Locator = (By.CSS_SELECTOR, "#content table a.btn-danger")
    # Stock OpenCart confirms actions with a green banner above the content.
    SUCCESS_BANNER: Locator = (By.CSS_SELECTOR, ".alert-success")

    def open(self, route: str = "account/wishlist") -> Self:
        super().open(route)
        return self

    def product_names(self) -> list[str]:
        """
        Names of the saved products, in row order, e.g. ['iPhone'].
        Empty once the wish list is cleared.
        """
        names: list[str] = []
        for row in self.driver.find_elements(*self.TABLE_ROW):
            cells = row.find_elements(By.CSS_SELECTOR, "td")
            # The name cell sits next to the image cell.
            if len(cells) > 1:
                names.append(cells[1].text.strip())
        return names

    def has_product(self, name: str) -> bool:
        return name in self.product_names()

    def remove(self, name: str) -> Self:
        """
        Click a product's remove link and wait until it is no longer listed.
        """
        index = self.product_names().index(name)
        self.driver.find_elements(*self.REMOVE_LINK)[index].click()
        # Removing navigates; mid-reload the DOM briefly has no table at
        # all, so settle on the new page before callers read it again.
        self.wait.until(lambda d: name not in self.product_names())
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        return self

    def success_text(self) -> str:
        """
        Text of the green response banner, e.g. 'Success: You have modified
        your wish list!'.
        """
        texts = [t.text for t in self.driver.find_elements(*self.SUCCESS_BANNER) if t.text.strip()]
        return "\n".join(texts).strip()
