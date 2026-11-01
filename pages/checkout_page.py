"""
Author: Monark

Checkout page (F15): https://opencart.abstracta.us/index.php?route=checkout/checkout

Stock OpenCart 3 checkout is a single page with collapsible steps:
  1 Checkout Options -> 2 Billing Details -> (3 Delivery Details) ->
  4 Delivery Method -> 5 Payment Method -> 6 Confirm Order
Each step loads via AJAX, so every 'continue' waits for the next panel.
"""

from typing import Self

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage, Locator


class CheckoutPage(BasePage):
    # Step 1 - Checkout Options
    GUEST_RADIO: Locator = (By.CSS_SELECTOR, "input[name='account'][value='guest']")
    ACCOUNT_CONTINUE: Locator = (By.ID, "button-account")
    # Step 2 - Billing Details (guest form)
    FIRST_NAME: Locator = (By.ID, "input-payment-firstname")
    LAST_NAME: Locator = (By.ID, "input-payment-lastname")
    EMAIL: Locator = (By.ID, "input-payment-email")
    TELEPHONE: Locator = (By.ID, "input-payment-telephone")
    ADDRESS_1: Locator = (By.ID, "input-payment-address-1")
    CITY: Locator = (By.ID, "input-payment-city")
    POSTCODE: Locator = (By.ID, "input-payment-postcode")
    COUNTRY: Locator = (By.ID, "input-payment-country")
    REGION: Locator = (By.ID, "input-payment-zone")
    GUEST_CONTINUE: Locator = (By.ID, "button-guest")
    FIELD_ERRORS: Locator = (By.CSS_SELECTOR, "#collapse-payment-address .text-danger")
    # Step 4 - Delivery Method
    SHIPPING_CONTINUE: Locator = (By.ID, "button-shipping-method")
    # Step 5 - Payment Method
    AGREE_CHECKBOX: Locator = (By.CSS_SELECTOR, "input[name='agree']")
    PAYMENT_CONTINUE: Locator = (By.ID, "button-payment-method")
    WARNING: Locator = (By.CSS_SELECTOR, ".alert-danger")

    def open(self, route: str = "checkout/checkout") -> Self:
        super().open(route)
        return self

    def is_on_checkout(self) -> bool:
        return "checkout/checkout" in self.driver.current_url

    # --- step 1 ------------------------------------------------------------

    def choose_guest_checkout(self) -> Self:
        self.click(self.GUEST_RADIO)
        self.click(self.ACCOUNT_CONTINUE)
        # The billing panel slides open once the AJAX call returns.
        self.wait.until(ec.element_to_be_clickable(self.GUEST_CONTINUE))
        return self

    # --- step 2 ------------------------------------------------------------

    def fill_billing(self, details: dict[str, str]) -> Self:
        self.type(self.FIRST_NAME, details["first_name"])
        self.type(self.LAST_NAME, details["last_name"])
        self.type(self.EMAIL, details["email"])
        self.type(self.TELEPHONE, details["telephone"])
        self.type(self.ADDRESS_1, details["address_1"])
        self.type(self.CITY, details["city"])
        self.type(self.POSTCODE, details["postcode"])
        Select(self.find(self.COUNTRY)).select_by_visible_text(details["country"])
        # The region list is reloaded after the country changes.
        self.wait.until(
            lambda d: any(
                o.text.strip() == details["region"]
                for o in Select(d.find_element(*self.REGION)).options
            )
        )
        Select(self.find(self.REGION)).select_by_visible_text(details["region"])
        return self

    def continue_billing(self) -> Self:
        self.click(self.GUEST_CONTINUE)
        # Either validation errors appear under the fields or the next step opens.
        self.wait.until(
            lambda d: d.find_elements(*self.FIELD_ERRORS)
            or d.find_elements(*self.SHIPPING_CONTINUE)
            and d.find_element(*self.SHIPPING_CONTINUE).is_displayed()
        )
        return self

    def field_errors(self) -> list[str]:
        """
        Visible per-field validation messages on the billing form.
        """
        return [e.text.strip() for e in self.find_all(self.FIELD_ERRORS) if e.is_displayed() and e.text.strip()]

    # --- step 4 ------------------------------------------------------------

    def continue_delivery_method(self) -> Self:
        self.click(self.SHIPPING_CONTINUE)
        self.wait.until(ec.element_to_be_clickable(self.PAYMENT_CONTINUE))
        return self

    # --- step 5 ------------------------------------------------------------

    def continue_payment_without_agreeing(self) -> str:
        """
        Click Continue on Payment Method with Terms & Conditions unticked and
        return the warning banner text.
        """
        agree = self.find(self.AGREE_CHECKBOX)
        if agree.is_selected():
            agree.click()
        self.click(self.PAYMENT_CONTINUE)
        self.wait.until(lambda d: any(w.is_displayed() and w.text.strip() for w in d.find_elements(*self.WARNING)))
        return "\n".join(w.text.strip() for w in self.find_all(self.WARNING) if w.is_displayed()).strip()
