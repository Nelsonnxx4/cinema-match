import pytest

from src.errors import ValidationError
from src.validation import (
    clean_text,
    normalize_genre_list,
    validate_genre,
    validate_movie_search,
)


def test_clean_text_strips_control_characters_and_extra_spacing():
    assert clean_text("  The\n\nMatrix\tReloaded  ") == "The Matrix Reloaded"


def test_clean_text_rejects_non_string_values():
    with pytest.raises(ValidationError, match="text value must be a string"):
        clean_text(123)


def test_validate_genre_accepts_supported_genres_case_insensitively():
    assert validate_genre(" action ")
    assert validate_genre("science   fiction")


def test_validate_genre_rejects_empty_and_unknown_genres():
    assert not validate_genre("")
    assert not validate_genre("Space Opera")


def test_validate_movie_search_returns_clean_query():
    assert validate_movie_search("  Spider-Man: No Way Home  ") == "Spider-Man: No Way Home"


def test_validate_movie_search_rejects_empty_queries():
    with pytest.raises(ValidationError, match="movie search is required"):
        validate_movie_search("   ")


def test_validate_movie_search_rejects_unsafe_characters():
    with pytest.raises(ValidationError, match="unsupported characters"):
        validate_movie_search("<script>alert('movie')</script>")


def test_normalize_genre_list_removes_duplicates_and_empty_values():
    genres = [" Action ", "action", "", "Comedy", " science   fiction "]

    assert normalize_genre_list(genres) == ["Action", "Comedy", "Science Fiction"]


def test_normalize_genre_list_rejects_unknown_genres():
    with pytest.raises(ValidationError, match="unsupported genre: Space Opera"):
        normalize_genre_list(["Action", "Space Opera"])


def test_normalize_genre_list_requires_at_least_one_valid_genre():
    with pytest.raises(ValidationError, match="select at least one genre"):
        normalize_genre_list(["", "   "])
