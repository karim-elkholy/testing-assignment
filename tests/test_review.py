"""
Author: Monark
Tester: Monark

T014 - Product Review (F13) - all 3 scenarios.

Function IDs/Names: F13 Product Review
(Reviews tab on the iPhone product page:
https://opencart.abstracta.us/index.php?route=product/product&product_id=40)

Scenario 1: a valid review (name, 25+ characters of text, rating) is accepted.
Scenario 2: review text shorter than 25 characters is rejected.
Scenario 3: a review with no star rating selected is rejected.
"""
from collections.abc import Callable
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver

from pages.review_section import ReviewSection

TEST_ID = "T014"

REVIEWER: str = "Test User"
# 25+ characters, so it passes the site's length rule.
VALID_TEXT: str = "This phone works well and the battery lasts all day."
# Under 25 characters, so it should be rejected.
SHORT_TEXT: str = "Good phone"


def _open_review_form(driver: WebDriver, base_url: str) -> ReviewSection:
    """Open the iPhone page and switch to the Reviews tab."""
    return ReviewSection(driver, base_url).open().open_reviews_tab()


def test_scenario_1_valid_review_is_accepted(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    review = _open_review_form(driver, base_url)

    # Fill in every field correctly with a 5-star rating and submit.
    review.fill(name=REVIEWER, text=VALID_TEXT, rating=5)
    review.submit()
    snap("t014_scenario_1")

    message: str = review.message().lower()
    assert "thank you for your review" in message, f"expected thank-you message, got {message!r}"


def test_scenario_2_short_review_text_is_rejected(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    review = _open_review_form(driver, base_url)

    # Review text is only 10 characters long.
    review.fill(name=REVIEWER, text=SHORT_TEXT, rating=4)
    review.submit()
    snap("t014_scenario_2")

    message: str = review.message().lower()
    assert "review text must be between 25 and 1000 characters" in message, (
        f"expected review-length warning, got {message!r}"
    )


def test_scenario_3_missing_rating_is_rejected(
    driver: WebDriver, base_url: str, snap: Callable[[str], Path]
) -> None:
    review = _open_review_form(driver, base_url)

    # Valid name and text, but no star rating is clicked.
    review.fill(name=REVIEWER, text=VALID_TEXT, rating=None)
    review.submit()
    snap("t014_scenario_3")

    message: str = review.message().lower()
    assert "please select a review rating" in message, f"expected rating warning, got {message!r}"
