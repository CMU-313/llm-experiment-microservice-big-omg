from src import translator
from src.translator import translate_content


def test_falls_back_to_original_content_when_llm_is_unavailable(monkeypatch):
    monkeypatch.setattr(translator, "OLLAMA_BASE_URL", "http://127.0.0.1:9")

    content = "这是一条中文消息"
    is_english, translated_content = translate_content(content)

    assert is_english is True
    assert translated_content == content


def test_llm_normal_response():
    pass


def test_llm_gibberish_response():
    pass
