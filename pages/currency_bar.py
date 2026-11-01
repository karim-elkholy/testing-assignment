"""
Author: Monark

Header currency switcher (F14), read against the product page price:
https://opencart.abstracta.us/index.php?route=product/product&product_id=40
"""

from typing import Self

from selenium.webdriver.common.by import By

from pages.base_page import BasePage, Locator
from pages.product_page import IPHONE_PRODUCT_ID

# Currency codes used by the stock OpenCart header form (button name= values).
EURO: str = "EUR"
POUND: str = "GBP"
US_DOLLAR: str = "USD"

# Symbol each currency shows in front of prices.
SYMBOLS: dict[str, str] = {EURO: "€", POUND: "£", US_DOLLAR: "$"}


class CurrencyBar(BasePage):
    # Stock OpenCart 3 header: <form id="form-currency"> with a Bootstrap
    # dropdown; each option is <button class="currency-select" name="EUR">.
    CURRENCY_TOGGLE: Locator = (By.CSS_SELECTOR, "#form-currency button.dropdown-toggle")
    CURRENCY_MENU: Locator = (By.CSS_SELECTOR, "#form-currency .dropdown-menu")
    # Main product price (incl. tax), e.g. '$123.20'.
    PRICE: Locator = (By.CSS_SELECTOR, "#content .list-unstyled h2")

    def open(self, route: str = f"product/product&product_id={IPHONE_PRODUCT_ID}") -> Self:
        super().open(route)
        return self

    @staticmethod
    def _option(code: str) -> Locator:
        return (By.CSS_SELECTOR, f"#form-currency button.currency-select[name='{code}']")

    def switch_to(self, code: str) -> Self:
        """
        Pick a currency ('EUR', 'GBP' or 'USD') from the header dropdown and
        wait until the product price shows that currency's symbol.
        """
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        self.click(self.CURRENCY_TOGGLE)
        self.click(self._option(code))
        # Submitting the currency form reloads the page.
        self.wait.until(lambda d: SYMBOLS[code] in self.price_text())
        return self

    def price_text(self) -> str:
        """
        Main product price as displayed, e.g. '$123.20' or '€97.14'.
        """
        return self.find(self.PRICE).text.strip()

    def header_cart_text(self) -> str:
        """
        Header cart summary, e.g. '0 item(s) - €0.00'.
        """
        return self.cart_summary()
