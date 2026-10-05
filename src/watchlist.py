"""Movie watchlist and watched-list module for Group 17.


Purpose:
- Manage movie results and movie details for user interaction.
- Allow users to add/remove movies from a watchlist.
- Track watched movies separately from still-to-watch movies.

Expected flow:
1. A movie is displayed to the user.
2. The user chooses to add it to the watchlist or mark it as watched.
3. The data is stored in JSON.
4. The UI reads the list and displays it to the user.

Recommended functions:
- add_to_watchlist(movie: dict) -> None
- remove_from_watchlist(movie_id: int) -> None
- get_watchlist() -> list[dict]
- mark_as_watched(movie: dict) -> None
- get_watched_movies() -> list[dict]

Important notes:
- Keep the movie object format consistent across the app.
- Handle duplicate entries carefully.
- Make sure this module works with the storage file layer and the UI.
"""

# NOTE FOR TEAM:
# This module is part of the user's movie interaction flow.
# It should not directly call the TMDB or Gemini APIs unless absolutely necessary.
# The focus is on user actions and local list management.

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.errors import StorageError, ValidationError
from src.storage import read_json_file, write_json_file
from src.validation import clean_text


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WATCHLIST_FILE = str(DATA_DIR / "watchlist.json")
WATCHED_FILE = str(DATA_DIR / "watched.json")


def add_to_watchlist(movie: dict, path: str = WATCHLIST_FILE) -> None:
    """Add a movie to the watchlist, replacing an older copy if it exists."""
    saved_movie = normalize_movie_for_list(movie)
    movies = get_watchlist(path)
    updated_movies = _add_or_replace_movie(movies, saved_movie)

    write_json_file(path, updated_movies)


def remove_from_watchlist(movie_id: int, path: str = WATCHLIST_FILE) -> None:
    """Remove a movie from the watchlist by its TMDB id."""
    movies = get_watchlist(path)
    updated_movies = []

    for movie in movies:
        if movie["id"] != movie_id:
            updated_movies.append(movie)

    write_json_file(path, updated_movies)


def get_watchlist(path: str = WATCHLIST_FILE) -> list[dict]:
    """Load all movies saved in the watchlist."""
    return _load_movie_list(path, "watchlist")


def mark_as_watched(
    movie: dict,
    watchlist_path: str = WATCHLIST_FILE,
    watched_path: str = WATCHED_FILE,
) -> None:
    """Move a movie into watched movies and remove it from the watchlist."""
    watched_movie = normalize_movie_for_list(movie)
    watched_movies = get_watched_movies(watched_path)
    updated_watched_movies = _add_or_replace_movie(watched_movies, watched_movie)

    write_json_file(watched_path, updated_watched_movies)
    remove_from_watchlist(watched_movie["id"], watchlist_path)


def get_watched_movies(path: str = WATCHED_FILE) -> list[dict]:
    """Load all movies marked as watched."""
    return _load_movie_list(path, "watched movies")


def is_in_watchlist(movie_id: int, path: str = WATCHLIST_FILE) -> bool:
    """Return True when a movie id already exists in the watchlist."""
    movies = get_watchlist(path)

    for movie in movies:
        if movie["id"] == movie_id:
            return True

    return False


def normalize_movie_for_list(movie: dict) -> dict:
    """Keep only the movie fields the local lists need."""
    if not isinstance(movie, dict):
        raise ValidationError("movie must be a dictionary")

    movie_id = movie.get("id")
    if isinstance(movie_id, str) and movie_id.isdigit():
        movie_id = int(movie_id)

    if not isinstance(movie_id, int) or movie_id <= 0:
        raise ValidationError("movie id is required")

    title = movie.get("title") or movie.get("name")
    if not isinstance(title, str) or not clean_text(title):
        raise ValidationError("movie title is required")

    saved_movie = {
        "id": movie_id,
        "title": clean_text(title),
        "overview": _clean_optional_text(movie.get("overview")),
        "release_date": _clean_optional_text(movie.get("release_date")),
        "year": _clean_optional_text(movie.get("year")),
        "rating": movie.get("rating") or movie.get("vote_average") or 0,
        "poster_path": _clean_optional_text(movie.get("poster_path")),
        "poster_url": _clean_optional_text(movie.get("poster_url")),
        "tmdb_url": _clean_optional_text(movie.get("tmdb_url")),
        "genres": _clean_genres(movie.get("genres")),
        "runtime": movie.get("runtime"),
    }

    if not saved_movie["year"]:
        saved_movie["year"] = _get_year_from_date(saved_movie["release_date"])

    return saved_movie


def _load_movie_list(path: str, list_name: str) -> list[dict]:
    data = read_json_file(path, [])

    if not isinstance(data, list):
        raise StorageError(f"Saved {list_name} data must be a list.")

    movies = []
    for movie in data:
        movies.append(normalize_movie_for_list(movie))

    return movies


def _add_or_replace_movie(movies: list[dict], new_movie: dict) -> list[dict]:
    updated_movies = []
    was_replaced = False

    for movie in movies:
        if movie["id"] == new_movie["id"]:
            updated_movies.append(new_movie)
            was_replaced = True
        else:
            updated_movies.append(movie)

    if not was_replaced:
        updated_movies.append(new_movie)

    return updated_movies


def _clean_optional_text(value: Any) -> str:
    if isinstance(value, str):
        return clean_text(value)
    return ""


def _clean_genres(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    genres = []
    for genre in value:
        if isinstance(genre, str) and clean_text(genre):
            genres.append(clean_text(genre))

    return genres


def _get_year_from_date(value: str) -> str:
    if isinstance(value, str) and len(value) >= 4 and value[:4].isdigit():
        return value[:4]
    return ""
