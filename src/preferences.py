"""User preferences module for Group 17.

Responsibility: Evalsam Gaul

Purpose:
- Save and load the user's selected movie genres.
- Keep preference data in a simple and consistent format.
- Pass the stored preferences to the AI recommendation system.

Expected flow:
1. The user selects preferred genres in the UI.
2. Preferences are validated and stored locally.
3. This module loads the saved preferences whenever recommendations are needed.
"""


from __future__ import annotations

from pathlib import Path

from src.errors import StorageError
from src.storage import read_json_file, write_json_file
from src.validation import normalize_genre_list


PREFERENCE_FILE = str(
    Path(__file__).resolve().parent.parent / "data" / "preference.json"
)
DEFAULT_PREFERENCES = {"genres": []}


def save_preferences(genres: list[str], path: str = PREFERENCE_FILE) -> None:
    """Validate and save the user's preferred genres."""
    normalized_genres = normalize_genre_list(genres)
    write_json_file(path, {"genres": normalized_genres})


def load_preferences(path: str = PREFERENCE_FILE) -> list[str]:
    """Load the user's saved preferred genres."""
    data = read_json_file(path, DEFAULT_PREFERENCES)

    if isinstance(data, list):
        return normalize_genre_list(data)

    if not isinstance(data, dict):
        raise StorageError("Preference data must be a JSON object.")

    genres = data.get("genres", [])
    if not genres:
        return []

    if not isinstance(genres, list):
        raise StorageError("Preference genres must be saved as a list.")

    return normalize_genre_list(genres)


def update_preferences(new_genres: list[str], path: str = PREFERENCE_FILE) -> list[str]:
    """Add new genres to the saved preferences and return the updated list."""
    saved_genres = load_preferences(path)
    combined_genres = saved_genres + new_genres
    normalized_genres = normalize_genre_list(combined_genres)

    write_json_file(path, {"genres": normalized_genres})
    return normalized_genres


def clear_preferences(path: str = PREFERENCE_FILE) -> None:
    """Reset the saved preferences to an empty genre list."""
    write_json_file(path, DEFAULT_PREFERENCES)
