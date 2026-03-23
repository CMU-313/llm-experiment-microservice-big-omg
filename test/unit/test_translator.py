from unittest.mock import patch

from src import translator
from src.translator import translate_content


def test_falls_back_to_original_content_when_llm_is_unavailable(monkeypatch):
    monkeypatch.setattr(translator, "OLLAMA_BASE_URL", "http://127.0.0.1:9")

    content = "这是一条中文消息"
    is_english, translated_content = translate_content(content)

    assert is_english is True
    assert translated_content == content


def test_llm_normal_response():
    with patch(
        "src.translator._query_ollama",
        return_value='{"is_english": false, "translated_content": "This is my first example."}',
    ):
        result = translate_content("Hier ist dein erstes Beispiel.")

    assert result == (False, "This is my first example.")


def test_llm_gibberish_response():
    with patch(
        "src.translator._query_ollama",
        return_value="I don't understand your request",
    ):
        result = translate_content("Hier ist dein erstes Beispiel.")

    assert result == (True, "Hier ist dein erstes Beispiel.")


class TestQueryLLMRobust:
    @patch("src.translator._query_ollama")
    def test_normal_english_post(self, mock_query):
        mock_query.return_value = (
            '{"is_english": true, "translated_content": "Hello, how are you?"}'
        )
        result = translate_content("Hello, how are you?")
        assert result == (True, "Hello, how are you?")

    @patch("src.translator._query_ollama")
    def test_normal_non_english_post(self, mock_query):
        mock_query.return_value = (
            '{"is_english": false, "translated_content": "This is my first example."}'
        )
        result = translate_content("Hier ist dein erstes Beispiel.")
        assert result == (False, "This is my first example.")

    @patch("src.translator._query_ollama")
    def test_unexpected_text_response(self, mock_query):
        mock_query.return_value = "Malformed response: I don't understand your request"
        result = translate_content("Hier ist dein erstes Beispiel.")
        assert result == (True, "Hier ist dein erstes Beispiel.")

    @patch("src.translator._query_ollama")
    def test_invalid_english_value(self, mock_query):
        mock_query.return_value = (
            '{"is_english": "<true or false>", "translated_content": "This is my first example."}'
        )
        result = translate_content("Hier ist dein erstes Beispiel.")
        assert result == (True, "Hier ist dein erstes Beispiel.")

    @patch("src.translator._query_ollama")
    def test_empty_response(self, mock_query):
        mock_query.return_value = '{"is_english": false, "translated_content": ""}'
        result = translate_content("Bonjour")
        assert result == (True, "Bonjour")

    @patch("src.translator._query_ollama")
    def test_api_exception(self, mock_query):
        mock_query.return_value = None
        result = translate_content("Hola")
        assert result == (True, "Hola")
