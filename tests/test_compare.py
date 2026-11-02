"""
Author: Karim Elkholy
Tester: Karim Elkholy

T008 - Product Compare (F8) - all 4 scenarios.

Function IDs/Names: F8 Product Compare
('Compare this Product' button on product pages and category tiles, table
at https://opencart.abstracta.us/index.php?route=product/compare)

Scenario 1: two products appear side by side with their own prices.
Scenario 2: removing one product leaves the other compared.
Scenario 3: at most four products are compared - a fifth replaces the
            oldest and 'Product Compare (4)' stays.
Scenario 4: the empty comparison page names the wrong context; expected
            failure recorded as Defect 6 (xfail).

F8 is independent of login: the comparison lives in the visitor's
session, so every scenario runs as a guest in its own fresh browser.

Drafted with AI assistance (Claude) and reviewed by the author.
"""
from collections.abc import Callable
from pathlib import Path

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from pages.category_page import CategoryPage
from pages.compare_page import ComparePage
from pages.product_page import (
    HP_LP3065_PRODUCT_ID,
    IPHONE_PRODUCT_ID,
    MACBOOK_AIR_PRODUCT_ID,
    MACBOOK_PRODUCT_ID,
    SONY_VAIO_PRODUCT_ID,
    ProductPage,
)

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


def test_scenario_1_compare_two_products(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    _add_to_compare(driver, base_url, IPHONE_PRODUCT_ID, IPHONE["Product"])
    _add_to_compare(driver, base_url, MACBOOK_PRODUCT_ID, MACBOOK["Product"])

    compare = ComparePage(driver, base_url).open()
    snap("t008_scenario_1")

    # Both products sit side by side, each with its own price.
    assert compare.product_names() == [IPHONE["Product"], MACBOOK["Product"]], (
        f"comparison should list iPhone and MacBook, got {compare.product_names()!r}"
    )
    assert compare.row_values("Price") == [IPHONE["Price"], MACBOOK["Price"]], (
        f"price row should show both prices, got {compare.row_values('Price')!r}"
    )


def test_scenario_2_remove_one_product(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    _add_to_compare(driver, base_url, IPHONE_PRODUCT_ID, IPHONE["Product"])
    _add_to_compare(driver, base_url, MACBOOK_PRODUCT_ID, MACBOOK["Product"])
    compare = ComparePage(driver, base_url).open()
    assert compare.product_names() == [IPHONE["Product"], MACBOOK["Product"]]

    # Remove the first column; the other product must survive.
    compare.remove(IPHONE["Product"])
    snap("t008_scenario_2")

    assert "modified your product comparison" in compare.success_text(), (
        f"expected the removal confirmation, got {compare.success_text()!r}"
    )
    assert compare.product_names() == [MACBOOK["Product"]], (
        f"only the MacBook should remain, got {compare.product_names()!r}"
    )


def test_scenario_3_four_product_limit(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    # Add four products from the Desktops category tiles, in this order.
    category = CategoryPage(driver, base_url).open()
    count = category.compare_count()
    for product_id in (
        IPHONE_PRODUCT_ID,
        MACBOOK_PRODUCT_ID,
        MACBOOK_AIR_PRODUCT_ID,
        SONY_VAIO_PRODUCT_ID,
    ):
        count += 1
        category.compare_tile(product_id, count)
    assert category.compare_count() == 4, "four products should be compared"

    # A fifth product: the counter stays at four - the oldest (the iPhone,
    # added first) is dropped. The counter cannot tell a dropped add from a
    # successful eviction (both leave it at four), so verify the eviction on
    # the compare page itself and re-click while the demo drops the add.
    expected = ["MacBook", "MacBook Air", "Sony VAIO", "HP LP3065"]
    compare: ComparePage | None = None
    for _ in range(3):
        category.click_compare_tile(HP_LP3065_PRODUCT_ID, "HP LP3065")
        compare = ComparePage(driver, base_url).open()
        if compare.product_names() == expected:
            break
    snap("t008_scenario_3")

    assert compare is not None and compare.product_names() == expected, (
        f"the oldest product should be dropped, got "
        f"{compare.product_names() if compare else []!r}"
    )


@pytest.mark.xfail(
    reason="Defect 6: the empty comparison page shows the shopping cart's "
    "'Your shopping cart is empty!' instead of 'You have not chosen any "
    "products to compare.'"
)
def test_scenario_4_empty_comparison_message(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    _add_to_compare(driver, base_url, IPHONE_PRODUCT_ID, IPHONE["Product"])
    compare = ComparePage(driver, base_url).open()
    compare.remove(IPHONE["Product"])
    snap("t008_scenario_4")

    # After clearing the comparison the page should say so - it does not
    # (recorded as Defect 6), which is exactly what this xfail pins down.
    assert compare.contains_text("You have not chosen any products to compare.")
