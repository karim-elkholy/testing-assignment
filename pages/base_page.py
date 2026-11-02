"""
Author: Karim Elkholy

Base page: shared waits/helpers plus the site header (My account menu, cart summary).
"""

import re
from typing import Self

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

TIMEOUT: int = 15

# A Selenium locator, e.g. (By.ID, "input-email").
Locator = tuple[str, str]


class BasePage:
    # Stock OpenCart header (Bootstrap 3): the My Account dropdown toggles on
    # click and its parent <li> carries class 'open' while expanded.
    MY_ACCOUNT_TOGGLE: Locator = (By.CSS_SELECTOR, "#top-links a[title='My Account']")
    MENU_LOGIN: Locator = (By.CSS_SELECTOR, "#top-links .dropdown-menu a[href*='account/login']")
    MENU_REGISTER: Locator = (By.CSS_SELECTOR, "#top-links .dropdown-menu a[href*='account/register']")
    MENU_LOGOUT: Locator = (By.CSS_SELECTOR, "#top-links .dropdown-menu a[href*='account/logout']")
    # Header cart summary, e.g. '1 item(s) - $123.20'.
    CART_SUMMARY: Locator = (By.ID, "cart-total")

    def __init__(self, driver: WebDriver, base_url: str) -> None:
        self.driver: WebDriver = driver
        self.base_url: str = base_url.rstrip("/")
        # Polls may race with page reloads; stale/missing elements just mean
        # "not yet" and the poll retries.
        self.wait: WebDriverWait = WebDriverWait(
            driver,
            TIMEOUT,
            ignored_exceptions=(NoSuchElementException, StaleElementReferenceException),
        )

    # --- low-level helpers -------------------------------------------------

    def open(self, route: str = "common/home") -> Self:
        """
        Load a page by its OpenCart route, e.g. 'account/login'.
        """
        self.driver.get(f"{self.base_url}?route={route}")
        return self

    def find(self, locator: Locator) -> WebElement:
        return self.wait.until(ec.visibility_of_element_located(locator))

    def find_all(self, locator: Locator) -> list[WebElement]:
        return self.driver.find_elements(*locator)

    def click(self, locator: Locator) -> None:
        self.wait.until(ec.element_to_be_clickable(locator)).click()

    def type(self, locator: Locator, text: str) -> None:
        field: WebElement = self.find(locator)
        field.clear()
        field.send_keys(text)

    def contains_text(self, text: str) -> bool:
        body: WebElement = self.driver.find_element(By.TAG_NAME, "body")
        return text.lower() in body.text.lower()

    # --- site header -------------------------------------------------------

    def open_my_account_menu(self, item: Locator) -> Self:
        """
        Click-open the My account dropdown and wait for `item` to be clickable.

        The stock Bootstrap 3 dropdown toggles on click (the toggle's href is
        suppressed by Bootstrap) and the parent <li> carries class 'open' while
        expanded. `item` is the specific menu entry we intend to click next.
        """
        # Clicking mid-page-load lands nowhere; wait for the page to settle.
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        toggle: WebElement = self.wait.until(ec.element_to_be_clickable(self.MY_ACCOUNT_TOGGLE))
        item_wait = WebDriverWait(self.driver, 4)
        last_error: TimeoutException | None = None
        for _ in range(3):
            # The click toggles, so only click while the menu is closed.
            if not self._menu_is_open(toggle):
                toggle.click()
            try:
                item_wait.until(ec.element_to_be_clickable(item))
                return self
            except TimeoutException as exc:
                last_error = exc
                # Drop any half-open state so the next attempt re-opens cleanly.
                self.driver.execute_script(
                    "arguments[0].closest('li').classList.remove('open')", toggle
                )
        assert last_error is not None
        raise last_error

    def _menu_is_open(self, toggle: WebElement) -> bool:
        return bool(
            self.driver.execute_script(
                "return arguments[0].closest('li').classList.contains('open')", toggle
            )
        )

    def go_to_login(self) -> Self:
        """
        Open the Login page through the My account dropdown.
        """
        self.open_my_account_menu(self.MENU_LOGIN)
        self.click(self.MENU_LOGIN)
        return self

    def go_to_register(self) -> Self:
        """
        Open the Registration page through the My account dropdown.
        """
        self.open_my_account_menu(self.MENU_REGISTER)
        self.click(self.MENU_REGISTER)
        return self

    def logout(self) -> Self:
        """
        Log out through the My account dropdown (only when logged in).
        """
        self.open_my_account_menu(self.MENU_LOGOUT)
        self.click(self.MENU_LOGOUT)
        self.wait.until(lambda d: "account/logout" in d.current_url)
        return self

    def my_account_menu_routes(self) -> list[str]:
        """
        Route part of every link inside the My account dropdown, e.g.
        ['account/register', 'account/login'] when logged out. The links
        sit in the header DOM (hidden) even while the menu is closed.
        """
        routes: list[str] = []
        for link in self.driver.find_elements(By.CSS_SELECTOR, "#top-links .dropdown-menu a"):
            href = link.get_attribute("href") or ""
            if "route=" in href:
                routes.append(href.split("route=")[-1])
        return routes

    # --- header cart -------------------------------------------------------

    def cart_summary(self) -> str:
        """
        Header cart text, e.g. '1 item(s) - $123.20'.
        """
        for summary in self.find_all(self.CART_SUMMARY):
            if summary.is_displayed():
                return summary.text.strip()
        return ""

    def cart_badge_count(self) -> str:
        """
        Item count in the header cart summary ('1 item(s) - $123.20' -> '1').
        """
        match = re.search(r"\d+", self.cart_summary())
        return match.group(0) if match else ""
