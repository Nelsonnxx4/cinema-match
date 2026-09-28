from types import SimpleNamespace

import pytest

from src.ai import (
    build_recommendation_prompt,
    format_ai_response,
    get_ai_recommendations,
)
from src.errors import APIError


class FakeModels:
    def __init__(self):
        self.request = None

    def generate_content(self, **kwargs):
        self.request = kwargs
        return SimpleNamespace(
            text='[{"title": "Arrival", "reason": "It blends science fiction with emotion."}]'
        )


class FakeClient:
    def __init__(self):
        self.models = FakeModels()


def test_build_recommendation_prompt_includes_preferences_and_watchlist():
    prompt = build_recommendation_prompt(
        ["Science Fiction", "Drama"],
        [{"title": "Interstellar", "release_date": "2014-11-07"}],
    )

    assert "Science Fiction" in prompt
    assert "Drama" in prompt
    assert "Interstellar" in prompt
    assert "Return only valid JSON" in prompt


def test_format_ai_response_parses_json_recommendations():
    response = format_ai_response(
        """
        [
          {"title": "The Prestige", "reason": "It has mystery and strong twists."}
        ]
        """
    )

    assert response == [
        {"title": "The Prestige", "reason": "It has mystery and strong twists."}
    ]


def test_format_ai_response_parses_json_inside_markdown_fence():
    response = format_ai_response(
        """
        ```json
        [{"title": "Soul", "reason": "It is thoughtful and heartfelt."}]
        ```
        """
    )

    assert response == [{"title": "Soul", "reason": "It is thoughtful and heartfelt."}]


def test_format_ai_response_rejects_unreadable_text():
    with pytest.raises(APIError, match="unreadable format"):
        format_ai_response("Here are some movies you may like.")


def test_get_ai_recommendations_uses_client_and_formats_response():
    client = FakeClient()

    recommendations = get_ai_recommendations(
        ["Science Fiction"],
        [],
        api_key="test-key",
        client=client,
    )

    assert recommendations == [
        {"title": "Arrival", "reason": "It blends science fiction with emotion."}
    ]
    assert client.models.request["model"] == "gemini-2.0-flash"
    assert "Science Fiction" in client.models.request["contents"]


def test_get_ai_recommendations_requires_api_key_without_client(monkeypatch):
    monkeypatch.setattr("src.ai.load_dotenv", lambda: None)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    with pytest.raises(APIError, match="Gemini API key is missing"):
        get_ai_recommendations(["Comedy"], [])
