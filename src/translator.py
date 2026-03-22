import json
import os
import re
from urllib import error, request


OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b-instruct")
OLLAMA_TIMEOUT_SECONDS = float(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "30"))

PROMPT_TEMPLATE = """You are a translation service for a web forum.

Determine whether the following text is already in English. If it is not in English,
translate it into natural English.

Return JSON only with this exact schema:
{{"is_english": true, "translated_content": "original or translated text"}}

Rules:
- Return valid JSON only.
- Use true or false for is_english.
- If the text is already English, translated_content must be the original text unchanged.
- Do not include markdown, code fences, or explanations.

Text:
{content}
"""


def _extract_json_object(raw_response: str) -> dict | None:
    try:
        parsed = json.loads(raw_response)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", raw_response, re.DOTALL)
    if not match:
        return None

    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

    return parsed if isinstance(parsed, dict) else None


def _query_ollama(content: str) -> str | None:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": PROMPT_TEMPLATE.format(content=content),
        "stream": False,
        "options": {"temperature": 0},
    }
    body = json.dumps(payload).encode("utf-8")
    ollama_request = request.Request(
        f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(ollama_request, timeout=OLLAMA_TIMEOUT_SECONDS) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except (error.URLError, TimeoutError, json.JSONDecodeError):
        return None

    llm_text = response_payload.get("response")
    return llm_text if isinstance(llm_text, str) else None


def translate_content(content: str) -> tuple[bool, str]:
    if not content:
        return True, content

    llm_text = _query_ollama(content)
    if llm_text is None:
        return True, content

    parsed = _extract_json_object(llm_text)
    if parsed is None:
        return True, content

    is_english = parsed.get("is_english")
    translated_content = parsed.get("translated_content")
    if not isinstance(is_english, bool) or not isinstance(translated_content, str):
        return True, content
    if not translated_content.strip():
        return True, content

    return is_english, translated_content
