"""
Author: Daniel

Account Logout page: https://opencart.abstracta.us/index.php?route=account/logout
"""

from typing import Self

from selenium.webdriver.common.by import By

from pages.base_page import BasePage, Locator

LOGGED_OFF_MESSAGE: str = "You have been logged off your account"


class LogoutPage(BasePage):
    CONTENT: Locator = (By.ID, "content")

    def open(self, route: str = "account/logout") -> Self:
        super().open(route)
        return self

    def message(self) -> str:
        """
        Body text of the logout page (the 'logged off' confirmation).
        """
        return self.find(self.CONTENT).text.strip()

    def header_shows_guest_menu(self) -> bool:
        """
        True when the My Account dropdown offers Login/Register and NO Logout,
        i.e. the header shows the visitor as logged out.
        """
        self.open_my_account_menu(self.MENU_LOGIN)  # opens the menu, waits for 'Login'
        logout_links = [a for a in self.find_all(self.MENU_LOGOUT) if a.is_displayed()]
        register_links = [a for a in self.find_all(self.MENU_REGISTER) if a.is_displayed()]
        return not logout_links and bool(register_links)
