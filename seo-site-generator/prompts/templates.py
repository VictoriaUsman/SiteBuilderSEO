LOCAL_SEO_PAGE = """You are an expert local SEO copywriter. Generate a complete, high-converting local service page.

Service: {service}
City: {city}
Keyword: {keyword}
Domain: {domain}

Return ONLY valid JSON with this exact structure:
{{
  "title_tag": "...",
  "meta_description": "...",
  "slug": "...",
  "h1": "...",
  "intro_paragraph": "...",
  "h2_sections": [
    {{"heading": "...", "content": "..."}}
  ],
  "faq": [
    {{"question": "...", "answer": "..."}}
  ],
  "cta": "...",
  "image_alt_text": "...",
  "image_search_query": "...",
  "internal_link_suggestions": ["...", "..."]
}}

Rules:
- title_tag: include city + service + brand signal, max 60 chars
- meta_description: compelling, include city + service, max 160 chars
- slug: lowercase hyphenated, e.g. roof-repair-dallas
- h1: must contain the exact keyword "{keyword}" and city "{city}"
- intro_paragraph: keyword in first sentence, 80-120 words
- h2_sections: 4-6 sections covering benefits, process, local signals, trust
- faq: 5 questions local searchers actually ask
- cta: action-oriented, mention city
- image_alt_text: descriptive, include service and city
- image_search_query: 3-4 word phrase for stock photo search
- internal_link_suggestions: 2-4 related page slugs on same domain
- Minimum total body content: {min_words} words
"""

FAQ_SCHEMA_TEMPLATE = """<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": {faq_json}
}}
</script>"""

LOCAL_BUSINESS_SCHEMA = """<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "{business_name}",
  "description": "{description}",
  "address": {{
    "@type": "PostalAddress",
    "addressLocality": "{city}",
    "addressRegion": "{state}"
  }},
  "url": "{url}"
}}
</script>"""
