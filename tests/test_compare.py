"""
Author: Karim Elkholy
Tester: Karim Elkholy

T008 - Product Compare (F8) - all 3 scenarios.

Function IDs/Names: F8 Product Compare
('Compare this Product' button on a product page, table at
https://opencart.abstracta.us/index.php?route=product/compare)

Scenario 1: adding a product lists it with its price, model, brand and
            availability.
Scenario 2: a second product appears beside it with its own values.
Scenario 3: removing products empties the comparison again.

F8 is independent of login: the comparison lives in the visitor's
session, so every scenario runs as a guest in its own fresh browser.

Drafted with AI assistance (Claude) and reviewed by the author.
"""
from collections.abc import Callable
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver

from pages.compare_page import ComparePage
from pages.product_page import IPHONE_PRODUCT_ID, MACBOOK_PRODUCT_ID, ProductPage

TEST_ID = "T008"

# Demo-catalogue values as of Nov 2026 (verified against the live table).
IPHONE: dict[str, str] = {
    "Product": "iPhone",
    "Price": "$123.20",
    "Model": "product 11",
    "Brands": "Apple",
    "Availability": "In Stock",
}
MACBOOK: dict[str, str] = {
    "Product": "MacBook",
    "Price": "$602.00",
    "Availability": "Out Of Stock",
}


def _compare_page(driver: WebDriver, base_url: str) -> ComparePage:
    return ComparePage(driver, base_url).open()


def _add_to_compare(
    driver: WebDriver, base_url: str, product_id: int, name: str, attempts: int = 3
) -> ComparePage:
    """
    Add `product_id` to the comparison and return the compare page once the
    product is actually listed.

    The shared demo occasionally loses a compare add on its loaded
    backends: the success banner shows, but the product never appears
    (and a cache-busted re-read confirms it was the write, not the read).
    So each add is confirmed against the compare page and retried.
    """
    compare: ComparePage | None = None
    for _ in range(attempts):
        ProductPage(driver, base_url, product_id).open().compare_this_product()
        compare = ComparePage(driver, base_url).open()
        if name in compare.product_names():
            return compare
    listed = compare.product_names() if compare else []
    raise AssertionError(f"{name} never appeared in the comparison (last listing: {listed!r})")


def test_scenario_1_add_product_to_comparison(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    # Choose 'Compare this Product' on the iPhone page.
    compare = _add_to_compare(driver, base_url, IPHONE_PRODUCT_ID, IPHONE["Product"])
    snap("t008_scenario_1")

    assert compare.product_names() == [IPHONE["Product"]], (
        f"comparison should list only the iPhone, got {compare.product_names()!r}"
    )
    # The comparison shows the product's price, model, brand and availability.
    for label, expected in IPHONE.items():
        if label == "Product":
            continue
        actual = compare.row_values(label)
        assert actual == [expected], f"row {label!r} should be [{expected!r}], got {actual!r}"


def test_scenario_2_compare_two_products(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    _add_to_compare(driver, base_url, IPHONE_PRODUCT_ID, IPHONE["Product"])
    _add_to_compare(driver, base_url, MACBOOK_PRODUCT_ID, MACBOOK["Product"])

    compare = _compare_page(driver, base_url)
    snap("t008_scenario_2")

    # Both products sit side by side, each with its own values.
    assert compare.product_names() == [IPHONE["Product"], MACBOOK["Product"]], (
        f"comparison should list iPhone and MacBook, got {compare.product_names()!r}"
    )
    assert compare.row_values("Price") == [IPHONE["Price"], MACBOOK["Price"]], (
        f"price row should show both prices, got {compare.row_values('Price')!r}"
    )
    assert compare.row_values("Availability") == [IPHONE["Availability"], MACBOOK["Availability"]], (
        f"availability row should differ per product, got {compare.row_values('Availability')!r}"
    )


def test_scenario_3_remove_products_from_comparison(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    _add_to_compare(driver, base_url, IPHONE_PRODUCT_ID, IPHONE["Product"])
    _add_to_compare(driver, base_url, MACBOOK_PRODUCT_ID, MACBOOK["Product"])
    compare = _compare_page(driver, base_url)
    assert compare.product_names() == [IPHONE["Product"], MACBOOK["Product"]]

    # Remove the first column; the other product must survive.
    compare.remove(IPHONE["Product"])
    assert compare.product_names() == [MACBOOK["Product"]], (
        f"only the MacBook should remain, got {compare.product_names()!r}"
    )

    # Remove the last one and the comparison is empty again.
    compare.remove(MACBOOK["Product"])
    snap("t008_scenario_3")
    assert compare.product_names() == [], (
        f"comparison should be empty, got {compare.product_names()!r}"
    )
