import json
import os
from typing import Optional
from dotenv import load_dotenv
from prompts.templates import LOCAL_SEO_PAGE

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
MIN_WORD_COUNT = int(os.getenv("MIN_WORD_COUNT", "800"))


def _parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def generate_page_gemini(keyword: str, city: str, service: str, domain: str, api_key: str = None) -> dict:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key or os.getenv("GEMINI_API_KEY"))
    prompt = LOCAL_SEO_PAGE.format(
        service=service, city=city, keyword=keyword, domain=domain, min_words=MIN_WORD_COUNT
    )
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    return _parse_json_response(response.text)


def generate_page_openai(keyword: str, city: str, service: str, domain: str, api_key: str = None) -> dict:
    from openai import OpenAI

    client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    prompt = LOCAL_SEO_PAGE.format(
        service=service, city=city, keyword=keyword, domain=domain, min_words=MIN_WORD_COUNT
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def generate_page(keyword: str, city: str, service: str, domain: str, provider: Optional[str] = None,
                  gemini_key: str = None, openai_key: str = None) -> dict:
    p = (provider or AI_PROVIDER).lower()
    if p == "openai":
        return generate_page_openai(keyword, city, service, domain, api_key=openai_key)
    return generate_page_gemini(keyword, city, service, domain, api_key=gemini_key)
