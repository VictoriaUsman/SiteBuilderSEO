import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from seo.validator import validate_page, validate_batch


GOOD_CONTENT = {
    "title_tag": "Roof Repair Dallas | Fast Local Roofers",
    "meta_description": "Need roof repair in Dallas? Our licensed roofers offer same-day service. Free estimates. Call now.",
    "slug": "roof-repair-dallas",
    "h1": "Expert Roof Repair in Dallas, TX",
    "intro_paragraph": "Looking for reliable roof repair in Dallas? Our certified team delivers fast, affordable roofing solutions for homeowners across the Dallas area.",
    "h2_sections": [
        {"heading": "Why Choose Us", "content": "20 years of experience serving Dallas homeowners with quality roofing."},
        {"heading": "Our Process", "content": "We inspect, quote, and repair your roof within 48 hours."},
        {"heading": "Common Roof Problems", "content": "Hail damage, leaks, and missing shingles are our specialty."},
        {"heading": "Dallas Weather and Your Roof", "content": "Texas storms demand durable roofing materials."},
    ],
    "faq": [
        {"question": "How much does roof repair cost in Dallas?", "answer": "Typical repairs range from $300 to $1,500 depending on damage extent."},
        {"question": "Do you offer emergency roofing?", "answer": "Yes, we have 24/7 emergency roof repair available in Dallas."},
        {"question": "How long does roof repair take?", "answer": "Most repairs are completed in one day."},
        {"question": "Are you licensed in Texas?", "answer": "Yes, fully licensed and insured in the state of Texas."},
        {"question": "Do you work with insurance?", "answer": "Yes, we handle all insurance claims directly."},
    ],
    "cta": "Call us today for a free roof inspection in Dallas!",
    "image_alt_text": "Professional roofer repairing a damaged roof in Dallas Texas",
    "image_search_query": "roof repair workers",
    "internal_link_suggestions": ["emergency-roofing-dallas", "roof-inspection-dallas"],
}


def test_valid_page_passes():
    result = validate_page(GOOD_CONTENT, "roof repair")
    assert result.passed
    assert not result.errors


def test_missing_h1_fails():
    bad = {**GOOD_CONTENT, "h1": ""}
    result = validate_page(bad, "roof repair")
    assert not result.passed
    assert any("H1" in e for e in result.errors)


def test_keyword_not_in_h1_fails():
    bad = {**GOOD_CONTENT, "h1": "Best Contractors in Texas"}
    result = validate_page(bad, "roof repair")
    assert not result.passed


def test_title_too_long_fails():
    bad = {**GOOD_CONTENT, "title_tag": "A" * 70}
    result = validate_page(bad, "roof repair")
    assert not result.passed


def test_meta_too_long_fails():
    bad = {**GOOD_CONTENT, "meta_description": "A" * 170}
    result = validate_page(bad, "roof repair")
    assert not result.passed


def test_slug_with_spaces_fails():
    bad = {**GOOD_CONTENT, "slug": "roof repair dallas"}
    result = validate_page(bad, "roof repair")
    assert not result.passed


def test_duplicate_slugs_detected():
    results = [
        {"content": {**GOOD_CONTENT, "slug": "roof-repair-dallas"}, "row": {"keyword": "roof repair"}},
        {"content": {**GOOD_CONTENT, "slug": "roof-repair-dallas"}, "row": {"keyword": "roof repair"}},
    ]
    batch = validate_batch(results)
    assert "roof-repair-dallas" in batch["duplicate_slugs"]
