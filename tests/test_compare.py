"""
Author: Daniel

T008 - Product Compare (F8).

Function IDs/Names: F8 Product Compare
Tester: Daniel

Scenario 1: add two products -> both appear side by side with their own prices.
Scenario 2: remove one product -> success banner, only the other product remains.
Scenario 3: add a 5th product -> the list is capped at 4 and the oldest product is dropped.
Scenario 4: remove every product -> no table and an 'empty comparison' message.
            Marked xfail: the site shows the shopping cart's empty message instead
            (reported as a defect), so CI stays green while the defect is recorded.

No login needed (F8 is guest-accessible), so T008 can run first in parallel with T001/T002.
Each test opens a fresh browser, so every comparison starts empty.
"""
from collections.abc import Callable
from pathlib import Path

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from pages.category_page import CategoryPage
from pages.compare_page import ComparePage

TEST_ID = "T008"

# Products used (id: name, price shown incl. tax).
IPHONE, MACBOOK, MACBOOK_AIR, SONY_VAIO, HP_LP3065 = 40, 43, 44, 46, 47


def test_scenario_1_compare_two_products(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    compare = ComparePage(driver, base_url)

    # Input: click 'Compare this Product' on the iPhone page, then on the MacBook page.
    banner_1: str = compare.add_from_product_page(IPHONE)
    banner_2: str = compare.add_from_product_page(MACBOOK)
    assert "Success: You have added iPhone to your product comparison!" in banner_1, banner_1
    assert "Success: You have added MacBook to your product comparison!" in banner_2, banner_2

    # Expected output: both products are shown side by side with their own prices.
    compare.open()
    snap("t008_scenario_1")
    assert compare.product_names() == ["iPhone", "MacBook"]
    assert compare.row_values("Price") == ["$123.20", "$602.00"]


def test_scenario_2_remove_one_product(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    compare = ComparePage(driver, base_url)
    # Precondition: two products in the comparison.
    compare.add_from_product_page(IPHONE)
    compare.add_from_product_page(MACBOOK)
    compare.open()

    # Input: click 'Remove' under the iPhone column.
    banner: str = compare.remove(IPHONE)
    snap("t008_scenario_2")

    # Expected output: success banner and only the MacBook is left.
    assert "Success: You have modified your product comparison!" in banner, banner
    assert compare.product_names() == ["MacBook"]


def test_scenario_3_limit_of_four_products(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    compare = ComparePage(driver, base_url)
    CategoryPage(driver, base_url).open()  # Desktops category lists all five products

    # Input: add iPhone, MacBook, MacBook Air and Sony VAIO, then a 5th product (HP LP3065).
    for product_id in (IPHONE, MACBOOK, MACBOOK_AIR, SONY_VAIO):
        compare.add_from_category_page(product_id)
    assert compare.header_counter() == "Product Compare (4)", compare.header_counter()
    compare.add_from_category_page(HP_LP3065)
    snap("t008_scenario_3_1")

    # Expected output: the counter stays at 4 ...
    assert compare.header_counter() == "Product Compare (4)", compare.header_counter()
    # ... and the oldest product (iPhone) is dropped to make room for the newest.
    compare.open()
    snap("t008_scenario_3_2")
    assert compare.product_names() == ["MacBook", "MacBook Air", "Sony VAIO", "HP LP3065"]


@pytest.mark.xfail(
    strict=True,
    reason="Defect: empty comparison page shows 'Your shopping cart is empty!' "
    "instead of 'You have not chosen any products to compare.'",
)
def test_scenario_4_empty_comparison_message(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    compare = ComparePage(driver, base_url)
    compare.add_from_product_page(IPHONE)
    compare.open()

    # Input: remove the only product being compared.
    compare.remove(IPHONE)
    snap("t008_scenario_4")

    # Expected output: no comparison table, a Continue button, and an empty-comparison message.
    assert not compare.has_table(), "comparison table should disappear"
    assert compare.find(compare.CONTINUE).is_displayed()
    # This is the assertion that currently fails (see the xfail reason above).
    assert "You have not chosen any products to compare." in compare.content_text(), compare.content_text()
