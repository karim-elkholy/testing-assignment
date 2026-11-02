"""
Author: Monark

Header currency switcher (F14), read against the product page price:
https://opencart.abstracta.us/index.php?route=product/product&product_id=40
"""

from typing import Self

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage, Locator
from pages.product_page import IPHONE_PRODUCT_ID

# Currency codes used by the stock OpenCart header form (button name= values).
EURO: str = "EUR"
POUND: str = "GBP"
US_DOLLAR: str = "USD"

# Symbol each currency shows in front of prices.
SYMBOLS: dict[str, str] = {EURO: "€", POUND: "£", US_DOLLAR: "$"}

# The shared demo site is slow under sustained load: during one full-suite
# run the reload after submitting the currency form took past the page-wide
# 15s timeout, so the switch gets its own longer budget and one retry in
# case a submit is swallowed while the dropdown is still animating.
CURRENCY_RELOAD_TIMEOUT: int = 30


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
        reload_wait = WebDriverWait(
            self.driver,
            CURRENCY_RELOAD_TIMEOUT,
            ignored_exceptions=(NoSuchElementException, StaleElementReferenceException),
        )
        last_error: TimeoutException | None = None
        for _ in range(2):
            # The toggle click closes an open dropdown, so only click while
            # closed (matters on the retry, where no reload happened).
            toggle: WebElement = self.wait.until(ec.element_to_be_clickable(self.CURRENCY_TOGGLE))
            if not self._dropdown_is_open(toggle):
                toggle.click()
            self.click(self._option(code))
            # Submitting the currency form reloads the page.
            try:
                reload_wait.until(lambda d: SYMBOLS[code] in self.price_text())
                return self
            except TimeoutException as exc:
                last_error = exc
        assert last_error is not None
        raise last_error

    def _dropdown_is_open(self, toggle: WebElement) -> bool:
        """
        True while the currency dropdown is expanded (Bootstrap marks the
        wrapping .btn-group with class 'open'; unlike the My account menu
        there is no <li> in the currency form's ancestry).
        """
        return bool(
            self.driver.execute_script(
                "var g = arguments[0].closest('.btn-group') || arguments[0].closest('li');"
                "return g ? g.classList.contains('open') : false;",
                toggle,
            )
        )

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
