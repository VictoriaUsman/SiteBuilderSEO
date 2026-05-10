from dataclasses import dataclass, field

MAX_TITLE_LENGTH = 60
MAX_META_LENGTH = 160
MIN_WORD_COUNT = 800


@dataclass
class ValidationResult:
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_page(content: dict, keyword: str) -> ValidationResult:
    errors = []
    warnings = []

    title = content.get("title_tag", "")
    meta = content.get("meta_description", "")
    h1 = content.get("h1", "")
    intro = content.get("intro_paragraph", "")
    slug = content.get("slug", "")
    faq = content.get("faq", [])

    # Hard errors
    if not title:
        errors.append("Missing title_tag")
    elif len(title) > MAX_TITLE_LENGTH:
        errors.append(f"Title too long: {len(title)} chars (max {MAX_TITLE_LENGTH})")

    if not meta:
        errors.append("Missing meta_description")
    elif len(meta) > MAX_META_LENGTH:
        errors.append(f"Meta too long: {len(meta)} chars (max {MAX_META_LENGTH})")

    if not h1:
        errors.append("Missing H1")
    elif keyword.lower() not in h1.lower():
        errors.append(f"Keyword '{keyword}' not found in H1")

    if not intro:
        errors.append("Missing intro_paragraph")
    elif keyword.lower() not in intro.lower():
        warnings.append(f"Keyword '{keyword}' not in first paragraph")

    if not slug:
        errors.append("Missing slug")
    elif " " in slug or slug != slug.lower():
        errors.append(f"Slug has spaces or uppercase: '{slug}'")

    if not faq:
        warnings.append("No FAQ items — missing FAQ schema opportunity")

    # Word count estimate
    body_words = _count_words(content)
    if body_words < MIN_WORD_COUNT:
        warnings.append(f"Low word count: ~{body_words} words (min {MIN_WORD_COUNT})")

    if not content.get("image_alt_text"):
        warnings.append("Missing image_alt_text")

    return ValidationResult(passed=len(errors) == 0, errors=errors, warnings=warnings)


def _count_words(content: dict) -> int:
    text = " ".join([
        content.get("intro_paragraph", ""),
        " ".join(s.get("content", "") for s in content.get("h2_sections", [])),
        " ".join(q.get("answer", "") for q in content.get("faq", [])),
        content.get("cta", ""),
    ])
    return len(text.split())


def validate_batch(results: list[dict]) -> dict:
    all_slugs = [r["content"].get("slug", "") for r in results]
    all_titles = [r["content"].get("title_tag", "") for r in results]

    duplicate_slugs = {s for s in all_slugs if all_slugs.count(s) > 1}
    duplicate_titles = {t for t in all_titles if all_titles.count(t) > 1}

    return {
        "duplicate_slugs": list(duplicate_slugs),
        "duplicate_titles": list(duplicate_titles),
    }
