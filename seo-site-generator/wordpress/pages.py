import json
from wordpress.client import WordPressClient
from prompts.templates import FAQ_SCHEMA_TEMPLATE, LOCAL_BUSINESS_SCHEMA


def _build_faq_schema(faq: list[dict]) -> str:
    items = [
        {
            "@type": "Question",
            "name": q["question"],
            "acceptedAnswer": {"@type": "Answer", "text": q["answer"]},
        }
        for q in faq
    ]
    return FAQ_SCHEMA_TEMPLATE.format(faq_json=json.dumps(items, indent=2))


def _build_html_body(content: dict, internal_links: list[str], domain: str, include_schema: bool = True) -> str:
    sections_html = ""
    for section in content.get("h2_sections", []):
        sections_html += f"<h2>{section['heading']}</h2>\n<p>{section['content']}</p>\n\n"

    faq_html = "<h2>Frequently Asked Questions</h2>\n"
    for item in content.get("faq", []):
        faq_html += f"<h3>{item['question']}</h3>\n<p>{item['answer']}</p>\n\n"

    links_html = ""
    if internal_links:
        links_html = "<h2>Related Services</h2>\n<ul>\n"
        for slug in internal_links:
            label = slug.replace("-", " ").title()
            links_html += f'  <li><a href="https://{domain}/{slug}">{label}</a></li>\n'
        links_html += "</ul>\n"

    cta_html = f'<div class="cta-box"><p>{content.get("cta", "")}</p></div>\n'

    # WordPress.com strips <script> tags — omit schema to avoid raw JSON appearing on page
    schema = _build_faq_schema(content.get("faq", [])) if include_schema else ""

    return (
        f"<p>{content.get('intro_paragraph', '')}</p>\n\n"
        + sections_html
        + faq_html
        + links_html
        + cta_html
        + schema
    )


def create_page(
    client: WordPressClient,
    content: dict,
    featured_media_id: int | None,
    domain: str,
    parent_id: int | None = None,
    status: str = "publish",
    post_type: str = "posts",
) -> dict:
    internal_links = content.get("internal_link_suggestions", [])
    body_html = _build_html_body(content, internal_links, domain, include_schema=not client.is_wpcom)

    payload = {
        "title": content.get("h1", ""),
        "slug": content.get("slug", ""),
        "content": body_html,
        "excerpt": content.get("meta_description", ""),
        "status": status,
    }

    # Yoast SEO meta — only available on self-hosted WP with the plugin
    if not client.is_wpcom:
        payload["meta"] = {
            "yoast_head_json": {
                "title": content.get("title_tag", ""),
                "description": content.get("meta_description", ""),
            }
        }

    if featured_media_id:
        payload["featured_media"] = featured_media_id

    if parent_id:
        payload["parent"] = parent_id

    return client.post(post_type, payload)


def get_or_create_category(client: WordPressClient, name: str) -> int:
    existing = client.get("categories", params={"search": name})
    if existing:
        return existing[0]["id"]
    created = client.post("categories", {"name": name})
    return created["id"]
