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
