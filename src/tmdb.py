"""TMDB API integration guide for Group 17.

Purpose:
- Fetch movie recommendations from the TMDB API.
- Retrieve movie details for a selected title.
- Convert raw API responses into a clean format the rest of the app can use.

Expected flow:
1. The UI sends a genre or search request.
2. This module calls the TMDB endpoint.
3. The API response is cleaned and normalized.
4. Results are passed to the movie display/watchlist layers.

Recommended functions to implement:
- get_movies_by_genres(genres: list[str]) -> list[dict]
- get_movie_details(movie_id: int) -> dict
- normalize_movie_data(raw_movie: dict) -> dict

Important notes:
- Keep API logic separate from Streamlit UI code.
- Handle missing or invalid fields gracefully.
- Use environment variables for API keys and never hardcode secrets.
- Return predictable dictionaries so the UI and other modules can consume them.
"""

# NOTE FOR TEAM:
# This module should not contain UI logic or storage logic.
# It should only deal with external API calls and response formatting.
# If TMDB fails, return a helpful error message instead of crashing the app.

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
import requests

from src.errors import APIError, handle_api_error
from src.validation import normalize_genre_list, validate_movie_search


TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
DEFAULT_LANGUAGE = "en-US"
DEFAULT_TIMEOUT = 10

GENRE_IDS = {
    "Action": 28,
    "Adventure": 12,
    "Animation": 16,
    "Comedy": 35,
    "Crime": 80,
    "Documentary": 99,
    "Drama": 18,
    "Family": 10751,
    "Fantasy": 14,
    "History": 36,
    "Horror": 27,
    "Music": 10402,
    "Mystery": 9648,
    "Romance": 10749,
    "Science Fiction": 878,
    "TV Movie": 10770,
    "Thriller": 53,
    "War": 10752,
    "Western": 37,
}

GENRE_NAMES = {}
for genre_name, genre_id in GENRE_IDS.items():
    GENRE_NAMES[genre_id] = genre_name


def get_movies_by_genres(
    genres: list[str],
    page: int = 1,
    api_key: str | None = None,
    session: Any | None = None,
) -> list[dict]:
    """Fetch popular TMDB movies that match the selected genres."""
    normalized_genres = normalize_genre_list(genres)
    genre_ids = []

    for genre in normalized_genres:
        genre_ids.append(str(GENRE_IDS[genre]))

    data = _tmdb_get(
        "/discover/movie",
        {
            "with_genres": ",".join(genre_ids),
            "sort_by": "popularity.desc",
            "include_adult": "false",
            "include_video": "false",
            "language": DEFAULT_LANGUAGE,
            "page": page,
        },
        api_key=api_key,
        session=session,
    )

    return _normalize_results(data)


def search_movies(
    query: str,
    page: int = 1,
    api_key: str | None = None,
    session: Any | None = None,
) -> list[dict]:
    """Search TMDB movies by title."""
    cleaned_query = validate_movie_search(query)

    data = _tmdb_get(
        "/search/movie",
        {
            "query": cleaned_query,
            "include_adult": "false",
            "language": DEFAULT_LANGUAGE,
            "page": page,
        },
        api_key=api_key,
        session=session,
    )

    return _normalize_results(data)


def get_movie_details(
    movie_id: int,
    api_key: str | None = None,
    session: Any | None = None,
) -> dict:
    """Fetch full details for one TMDB movie."""
    if not isinstance(movie_id, int) or movie_id <= 0:
        raise APIError("Movie id must be a positive number.")

    data = _tmdb_get(
        f"/movie/{movie_id}",
        {"language": DEFAULT_LANGUAGE},
        api_key=api_key,
        session=session,
    )

    return normalize_movie_data(data)


def normalize_movie_data(raw_movie: dict) -> dict:
    """Convert a raw TMDB movie object into the app's movie format."""
    if not isinstance(raw_movie, dict):
        raise APIError("Movie data is not in the expected format.")

    movie_id = raw_movie.get("id")
    title = raw_movie.get("title") or raw_movie.get("original_title") or "Untitled"
    release_date = raw_movie.get("release_date") or ""
    poster_path = raw_movie.get("poster_path") or ""
    backdrop_path = raw_movie.get("backdrop_path") or ""
    genre_ids = raw_movie.get("genre_ids") or []
    genres = raw_movie.get("genres") or []

    if isinstance(genres, list) and genres and isinstance(genres[0], dict):
        genre_names = _extract_genre_names(genres)
    else:
        genre_names = _map_genre_ids_to_names(genre_ids)

    return {
        "id": movie_id,
        "title": title,
        "overview": raw_movie.get("overview") or "",
        "release_date": release_date,
        "year": _get_year_from_date(release_date),
        "rating": raw_movie.get("vote_average") or 0,
        "vote_count": raw_movie.get("vote_count") or 0,
        "popularity": raw_movie.get("popularity") or 0,
        "poster_path": poster_path,
        "poster_url": _build_image_url(poster_path),
        "backdrop_path": backdrop_path,
        "backdrop_url": _build_image_url(backdrop_path),
        "genres": genre_names,
        "genre_ids": genre_ids,
        "runtime": raw_movie.get("runtime"),
        "homepage": raw_movie.get("homepage") or "",
        "tmdb_url": _build_tmdb_url(movie_id),
    }


def _tmdb_get(
    endpoint: str,
    params: dict,
    api_key: str | None = None,
    session: Any | None = None,
) -> dict:
    api_key = _get_api_key(api_key)
    request_client = session or requests
    request_params = params.copy()
    request_params["api_key"] = api_key

    try:
        response = request_client.get(
            f"{TMDB_BASE_URL}{endpoint}",
            params=request_params,
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout as error:
        raise APIError(handle_api_error(TimeoutError())) from error
    except requests.exceptions.ConnectionError as error:
        raise APIError(handle_api_error(ConnectionError())) from error
    except requests.exceptions.RequestException as error:
        raise APIError(handle_api_error(error)) from error

    try:
        data = response.json()
    except ValueError as error:
        raise APIError("The movie service returned unreadable data.") from error

    if not isinstance(data, dict):
        raise APIError("The movie service returned data in an unexpected format.")

    return data


def _get_api_key(api_key: str | None = None) -> str:
    load_dotenv()
    key = api_key or os.getenv("TMDB_API_KEY")

    if not key:
        raise APIError("TMDB API key is missing. Add TMDB_API_KEY to your .env file.")

    return key


def _normalize_results(data: dict) -> list[dict]:
    results = data.get("results", [])
    if not isinstance(results, list):
        raise APIError("The movie service returned results in an unexpected format.")

    movies = []
    for movie in results:
        if isinstance(movie, dict):
            movies.append(normalize_movie_data(movie))

    return movies


def _build_image_url(path: str) -> str:
    if not path:
        return ""
    return f"{TMDB_IMAGE_BASE_URL}{path}"


def _build_tmdb_url(movie_id: Any) -> str:
    if not movie_id:
        return ""
    return f"https://www.themoviedb.org/movie/{movie_id}"


def _get_year_from_date(value: str) -> str:
    if isinstance(value, str) and len(value) >= 4 and value[:4].isdigit():
        return value[:4]
    return ""


def _extract_genre_names(genres: list) -> list[str]:
    genre_names = []

    for genre in genres:
        if isinstance(genre, dict) and isinstance(genre.get("name"), str):
            genre_names.append(genre["name"])

    return genre_names


def _map_genre_ids_to_names(genre_ids: list) -> list[str]:
    genre_names = []

    for genre_id in genre_ids:
        if genre_id in GENRE_NAMES:
            genre_names.append(GENRE_NAMES[genre_id])

    return genre_names
