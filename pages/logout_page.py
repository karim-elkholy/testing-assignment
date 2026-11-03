"""
Author: Karim Elkholy

Logout confirmation page (F9):
https://opencart.abstracta.us/index.php?route=account/logout
"""

from typing import Self

from selenium.webdriver.common.by import By

from pages.base_page import BasePage, Locator


class LogoutPage(BasePage):
    CONTENT: Locator = (By.ID, "content")

    def open(self, route: str = "account/logout") -> Self:
        super().open(route)
        return self

    def shows_confirmation(self) -> bool:
        """
        True once the logout page displays the logged-off message, e.g.
        'You have been logged off your account. It is now safe to leave
        the computer.' Also true when a guest opens the URL directly.
        """
        try:
            self.wait.until(lambda d: "account/logout" in self.driver.current_url)
            return "logged off your account" in self.find(self.CONTENT).text.lower()
        except Exception:
            return False
