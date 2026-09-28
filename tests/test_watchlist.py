import pytest

from src.errors import StorageError, ValidationError
from src.storage import write_json_file
from src.watchlist import (
    add_to_watchlist,
    get_watched_movies,
    get_watchlist,
    is_in_watchlist,
    mark_as_watched,
    normalize_movie_for_list,
    remove_from_watchlist,
)


def test_normalize_movie_for_list_keeps_expected_fields():
    movie = normalize_movie_for_list(
        {
            "id": "550",
            "title": " Fight Club ",
            "overview": "A restless office worker starts a club.",
            "release_date": "1999-10-15",
            "vote_average": 8.4,
            "genres": ["Drama", "Thriller"],
        }
    )

    assert movie["id"] == 550
    assert movie["title"] == "Fight Club"
    assert movie["year"] == "1999"
    assert movie["rating"] == 8.4
    assert movie["genres"] == ["Drama", "Thriller"]


def test_add_to_watchlist_saves_movie(tmp_path):
    path = tmp_path / "watchlist.json"

    add_to_watchlist({"id": 1, "title": "Arrival"}, str(path))

    assert get_watchlist(str(path)) == [
        {
            "id": 1,
            "title": "Arrival",
            "overview": "",
            "release_date": "",
            "year": "",
            "rating": 0,
            "poster_path": "",
            "poster_url": "",
            "tmdb_url": "",
            "genres": [],
            "runtime": None,
        }
    ]


def test_add_to_watchlist_replaces_duplicate_movie(tmp_path):
    path = tmp_path / "watchlist.json"
    add_to_watchlist({"id": 1, "title": "Arrival"}, str(path))
    add_to_watchlist({"id": 1, "title": "Arrival", "rating": 7.9}, str(path))

    watchlist = get_watchlist(str(path))

    assert len(watchlist) == 1
    assert watchlist[0]["rating"] == 7.9


def test_remove_from_watchlist_removes_by_id(tmp_path):
    path = tmp_path / "watchlist.json"
    add_to_watchlist({"id": 1, "title": "Arrival"}, str(path))
    add_to_watchlist({"id": 2, "title": "Soul"}, str(path))

    remove_from_watchlist(1, str(path))

    assert [movie["id"] for movie in get_watchlist(str(path))] == [2]


def test_mark_as_watched_moves_movie_from_watchlist(tmp_path):
    watchlist_path = tmp_path / "watchlist.json"
    watched_path = tmp_path / "watched.json"
    movie = {"id": 1, "title": "Arrival"}

    add_to_watchlist(movie, str(watchlist_path))
    mark_as_watched(movie, str(watchlist_path), str(watched_path))

    assert get_watchlist(str(watchlist_path)) == []
    assert get_watched_movies(str(watched_path))[0]["title"] == "Arrival"


def test_is_in_watchlist_returns_boolean(tmp_path):
    path = tmp_path / "watchlist.json"
    add_to_watchlist({"id": 1, "title": "Arrival"}, str(path))

    assert is_in_watchlist(1, str(path))
    assert not is_in_watchlist(2, str(path))


def test_watchlist_rejects_movie_without_id():
    with pytest.raises(ValidationError, match="movie id is required"):
        normalize_movie_for_list({"title": "Arrival"})


def test_get_watchlist_rejects_invalid_saved_shape(tmp_path):
    path = tmp_path / "watchlist.json"
    write_json_file(str(path), {"movies": []})

    with pytest.raises(StorageError, match="watchlist data must be a list"):
        get_watchlist(str(path))
