"""Validation and regex utilities for Group 17.

Responsibility: Henry Mshelia

Purpose:
- Clean user input before it is stored or used in API calls.
- Validate genre choices, search terms, and other user-provided values.
- Reuse common validation functions across the app to reduce bugs.

Expected flow:
1. User enters or selects information in the UI.
2. This module validates the data.
3. Only valid input reaches preferences, TMDB requests, or storage.

Recommended functions:
- clean_text(value: str) -> str
- validate_genre(value: str) -> bool
- validate_movie_search(query: str) -> str
- normalize_genre_list(genres: list[str]) -> list[str]

Important notes:
- Use Python's re module for pattern matching and cleaning.
- Reject empty strings and malformed input early.
- Keep validation error messages clear and user-friendly.
"""

# NOTE FOR TEAM:
# Validation should be reusable and simple.
# This module should not perform storage, TMDB calls, or AI logic.
# It should only answer: "Is this input valid and in the right format?"

from __future__ import annotations

import re

from src.errors import ValidationError


VALID_GENRES = (
    "Action",
    "Adventure",
    "Animation",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Family",
    "Fantasy",
    "History",
    "Horror",
    "Music",
    "Mystery",
    "Romance",
    "Science Fiction",
    "TV Movie",
    "Thriller",
    "War",
    "Western",
)

ALLOWED_SEARCH_CHARACTERS = "abcdefghijklmnopqrstuvwxyz"
ALLOWED_SEARCH_CHARACTERS += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALLOWED_SEARCH_CHARACTERS += "0123456789"
ALLOWED_SEARCH_CHARACTERS += " .,:'\"!?&()+/#-"


def clean_text(value: str) -> str:
    """Trim user text and collapse unusual spacing."""
    if not isinstance(value, str):
        raise ValidationError("text value must be a string")

    return re.sub(r"\s+", " ", value).strip()


def validate_genre(value: str) -> bool:
    """Return True when a value matches a supported movie genre."""
    try:
        genre = clean_text(value)
    except ValidationError:
        return False

    for valid_genre in VALID_GENRES:
        if genre.lower() == valid_genre.lower():
            return True

    return False


def validate_movie_search(query: str) -> str:
    """Clean and validate a movie search query."""
    cleaned_query = clean_text(query)

    if not cleaned_query:
        raise ValidationError("movie search is required")
    if len(cleaned_query) > 100:
        raise ValidationError("movie search must be 100 characters or fewer")

    for character in cleaned_query:
        if character not in ALLOWED_SEARCH_CHARACTERS:
            raise ValidationError("movie search contains unsupported characters")

    if not cleaned_query[0].isalnum():
        raise ValidationError("movie search must start with a letter or number")

    return cleaned_query


def normalize_genre_list(genres: list[str]) -> list[str]:
    """Clean, validate, and de-duplicate a list of selected genres."""
    if not isinstance(genres, list):
        raise ValidationError("genres must be provided as a list")

    normalized_genres: list[str] = []
    seen_genres: set[str] = set()
    invalid_genres: list[str] = []

    for genre in genres:
        try:
            cleaned_genre = clean_text(genre)
        except ValidationError:
            invalid_genres.append(str(genre))
            continue

        if not cleaned_genre:
            continue

        matched_genre = None
        for valid_genre in VALID_GENRES:
            if cleaned_genre.lower() == valid_genre.lower():
                matched_genre = valid_genre
                break

        if matched_genre is None:
            invalid_genres.append(cleaned_genre)
            continue

        if matched_genre not in seen_genres:
            normalized_genres.append(matched_genre)
            seen_genres.add(matched_genre)

    if invalid_genres:
        invalid = ", ".join(invalid_genres)
        raise ValidationError(f"unsupported genre: {invalid}")
    if not normalized_genres:
        raise ValidationError("select at least one genre")

    return normalized_genres
