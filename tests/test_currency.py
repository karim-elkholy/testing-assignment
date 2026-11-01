"""
Author: Monark
Tester: Monark

T013 - Currency Switch (F14) - all 3 scenarios.

Function IDs/Names: F14 Currency Switch
(header '$ Currency' dropdown, tested on the iPhone product page:
https://opencart.abstracta.us/index.php?route=product/product&product_id=40)

Scenario 1: switching to Euro shows every price with the EUR symbol.
Scenario 2: switching to Pound Sterling shows the price with the GBP symbol.
Scenario 3: switching to Euro and back to US Dollar restores exactly $123.20.

Each test opens a fresh browser, so every scenario starts in US Dollars.
"""
from collections.abc import Callable
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver

from pages.currency_bar import EURO, POUND, US_DOLLAR, CurrencyBar
from pages.product_page import IPHONE_PRODUCT_ID

TEST_ID = "T013"

# Default iPhone price in US Dollars (incl. tax), as seen in T004.
USD_PRICE: str = "$123.20"


def _open_iphone(driver: WebDriver, base_url: str) -> CurrencyBar:
    """Open the iPhone product page and confirm it starts in US Dollars."""
    page = CurrencyBar(driver, base_url).open(f"product/product&product_id={IPHONE_PRODUCT_ID}")
    assert page.price_text() == USD_PRICE, f"expected starting price {USD_PRICE}, got {page.price_text()!r}"
    return page


def test_scenario_1_switch_to_euro(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    page = _open_iphone(driver, base_url)

    # Choose '€ Euro' from the Currency dropdown.
    page.switch_to(EURO)
    snap("t013_scenario_1")

    price: str = page.price_text()
    # The product price and the header cart total must both use the Euro symbol.
    assert "€" in price and "$" not in price, f"price should be in Euro, got {price!r}"
    assert "€" in page.header_cart_text(), f"header cart should be in Euro, got {page.header_cart_text()!r}"


def test_scenario_2_switch_to_pound(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    page = _open_iphone(driver, base_url)

    # Choose '£ Pound Sterling' from the Currency dropdown.
    page.switch_to(POUND)
    snap("t013_scenario_2")

    price: str = page.price_text()
    # The price must use the Pound symbol and be a converted (different) amount.
    assert "£" in price and "$" not in price, f"price should be in Pound Sterling, got {price!r}"
    assert price != USD_PRICE, "converted price should differ from the US Dollar price"


def test_scenario_3_switch_back_to_dollar_restores_price(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    page = _open_iphone(driver, base_url)

    # Switch to Euro first and confirm the change happened.
    page.switch_to(EURO)
    assert "€" in page.price_text(), "price should be in Euro before switching back"

    # Then switch back to US Dollar.
    page.switch_to(US_DOLLAR)
    snap("t013_scenario_3")

    # The original price must come back exactly, with no rounding drift.
    assert page.price_text() == USD_PRICE, f"expected {USD_PRICE}, got {page.price_text()!r}"
