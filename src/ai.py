"""
Purpose:
- Use Gemini AI to provide personalized movie suggestions.
- Build a recommendation prompt from the user's preferences and saved movie context.
- Return movie suggestions and explanations that are useful to the user.

Expected flow:
1. Preferences and watchlist data are loaded.
2. A prompt is prepared with relevant user context.
3. Gemini is called with that prompt.
4. The response is formatted and shown in the UI.

Recommended functions:
- build_recommendation_prompt(preferences: list[str], watchlist: list[dict]) -> str
- get_ai_recommendations(preferences: list[str], watchlist: list[dict]) -> list[dict]
- format_ai_response(raw_response: str) -> list[dict]

Important notes:
- Keep prompts clear and specific.
- If the API call fails, show a friendly user-facing error.
- Do not expose raw API errors directly to the interface.
"""

# NOTE FOR TEAM:
# This module should rely on stored preferences and watchlist data.
# It should not own the user interface or file handling.
# The AI output should be easy to display in Streamlit cards or lists.

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from google import genai

from src.errors import APIError
from src.validation import clean_text


DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"


def build_recommendation_prompt(
    preferences: list[str],
    watchlist: list[dict],
) -> str:
    """Build a clear prompt for Gemini using user preferences and watchlist."""
    genres = _format_genres(preferences)
    watchlist_text = _format_watchlist(watchlist)

    return f"""
You are CinemaMatch, a helpful movie recommendation assistant.

User favorite genres:
{genres}

Movies already in the user's watchlist:
{watchlist_text}

Recommend 5 movies the user may enjoy.
Do not recommend movies already in the watchlist.
Keep each reason short and specific.

Return only valid JSON in this exact format:
[
  {{"title": "Movie title", "reason": "Why this movie fits the user"}}
]
""".strip()


def get_ai_recommendations(
    preferences: list[str],
    watchlist: list[dict],
    api_key: str | None = None,
    model: str = DEFAULT_GEMINI_MODEL,
    client: Any | None = None,
) -> list[dict]:
    """Ask Gemini for movie recommendations and return formatted results."""
    load_dotenv()
    gemini_api_key = (
        api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    )

    if not gemini_api_key and client is None:
        raise APIError(
            "Gemini API key is missing. Add GEMINI_API_KEY or GOOGLE_API_KEY to your .env file."
        )

    try:
        gemini_client = client or genai.Client(api_key=gemini_api_key)
        prompt = build_recommendation_prompt(preferences, watchlist)
        response = gemini_client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "temperature": 0.7,
                "max_output_tokens": 800,
            },
        )
        raw_response = getattr(response, "text", "")

        if not raw_response:
            raise APIError("Gemini did not return any recommendations.")

        return format_ai_response(raw_response)
    except APIError:
        raise
    except Exception as error:
        raise APIError(
            "AI recommendations are unavailable right now. Please try again later."
        ) from error


def format_ai_response(raw_response: str) -> list[dict]:
    """Convert Gemini JSON text into recommendation dictionaries."""
    if not raw_response or not raw_response.strip():
        raise APIError("Gemini did not return any recommendations.")

    parsed_data = _parse_json_from_text(raw_response)
    if isinstance(parsed_data, dict):
        parsed_data = parsed_data.get("recommendations", [])

    if not isinstance(parsed_data, list):
        raise APIError("Gemini returned recommendations in an unexpected format.")

    recommendations: list[dict] = []
    for item in parsed_data:
        if not isinstance(item, dict):
            continue

        title = item.get("title") or item.get("movie")
        reason = item.get("reason") or item.get("explanation") or item.get("why")

        if not isinstance(title, str) or not isinstance(reason, str):
            continue

        title = clean_text(title)
        reason = clean_text(reason)

        if title and reason:
            recommendations.append({"title": title, "reason": reason})

    if not recommendations:
        raise APIError("Gemini did not return usable recommendations.")

    return recommendations


def _format_genres(preferences: list[str]) -> str:
    cleaned_genres = []

    for genre in preferences:
        if isinstance(genre, str):
            cleaned_genre = clean_text(genre)
            if cleaned_genre:
                cleaned_genres.append(cleaned_genre)

    if not cleaned_genres:
        return "- No saved genres yet"

    return "\n".join(f"- {genre}" for genre in cleaned_genres)


def _format_watchlist(watchlist: list[dict]) -> str:
    if not watchlist:
        return "- No saved watchlist movies yet"

    movie_lines = []
    for movie in watchlist[:10]:
        if not isinstance(movie, dict):
            continue

        title = movie.get("title") or movie.get("name")
        if not isinstance(title, str):
            continue

        title = clean_text(title)
        year = movie.get("year") or _get_year_from_date(movie.get("release_date"))
        overview = movie.get("overview") or movie.get("description") or ""

        line = f"- {title}"
        if year:
            line += f" ({year})"
        if isinstance(overview, str) and overview.strip():
            line += f": {clean_text(overview)[:120]}"

        movie_lines.append(line)

    if not movie_lines:
        return "- No saved watchlist movies yet"

    return "\n".join(movie_lines)


def _get_year_from_date(value: Any) -> str:
    if isinstance(value, str) and len(value) >= 4 and value[:4].isdigit():
        return value[:4]
    return ""


def _parse_json_from_text(text: str) -> Any:
    cleaned_text = text.strip()

    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text.strip("`").strip()
        if cleaned_text.lower().startswith("json"):
            cleaned_text = cleaned_text[4:].strip()

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        start = cleaned_text.find("[")
        end = cleaned_text.rfind("]")

        if start == -1 or end == -1 or end <= start:
            raise APIError("Gemini returned recommendations in an unreadable format.")

        try:
            return json.loads(cleaned_text[start : end + 1])
        except json.JSONDecodeError as error:
            raise APIError(
                "Gemini returned recommendations in an unreadable format."
            ) from error
