import pytest
import requests

from src.errors import APIError
from src.tmdb import (
    get_movie_details,
    get_movies_by_genres,
    normalize_movie_data,
    search_movies,
)


class FakeResponse:
    def __init__(self, data, status_error=None):
        self.data = data
        self.status_error = status_error

    def raise_for_status(self):
        if self.status_error:
            raise self.status_error

    def json(self):
        return self.data


class FakeSession:
    def __init__(self, data):
        self.data = data
        self.last_request = None

    def get(self, url, params, timeout):
        self.last_request = {
            "url": url,
            "params": params,
            "timeout": timeout,
        }
        return FakeResponse(self.data)


def test_normalize_movie_data_for_search_result():
    movie = normalize_movie_data(
        {
            "id": 550,
            "title": "Fight Club",
            "overview": "An insomniac meets a soap salesman.",
            "release_date": "1999-10-15",
            "vote_average": 8.4,
            "genre_ids": [18, 53],
            "poster_path": "/poster.jpg",
        }
    )

    assert movie["id"] == 550
    assert movie["title"] == "Fight Club"
    assert movie["year"] == "1999"
    assert movie["genres"] == ["Drama", "Thriller"]
    assert movie["poster_url"].endswith("/poster.jpg")
    assert movie["tmdb_url"].endswith("/movie/550")


def test_get_movies_by_genres_calls_discover_endpoint():
    session = FakeSession(
        {
            "results": [
                {
                    "id": 1,
                    "title": "Mad Max",
                    "release_date": "1979-04-12",
                    "genre_ids": [28],
                }
            ]
        }
    )

    movies = get_movies_by_genres(["Action"], api_key="test-key", session=session)

    assert movies[0]["title"] == "Mad Max"
    assert session.last_request["url"].endswith("/discover/movie")
    assert session.last_request["params"]["with_genres"] == "28"
    assert session.last_request["params"]["api_key"] == "test-key"


def test_search_movies_calls_search_endpoint_with_clean_query():
    session = FakeSession({"results": [{"id": 2, "title": "Arrival"}]})

    movies = search_movies("  Arrival  ", api_key="test-key", session=session)

    assert movies[0]["title"] == "Arrival"
    assert session.last_request["url"].endswith("/search/movie")
    assert session.last_request["params"]["query"] == "Arrival"


def test_get_movie_details_calls_details_endpoint():
    session = FakeSession(
        {
            "id": 3,
            "title": "Interstellar",
            "release_date": "2014-11-07",
            "runtime": 169,
            "genres": [{"id": 878, "name": "Science Fiction"}],
        }
    )

    movie = get_movie_details(3, api_key="test-key", session=session)

    assert movie["title"] == "Interstellar"
    assert movie["runtime"] == 169
    assert movie["genres"] == ["Science Fiction"]
    assert session.last_request["url"].endswith("/movie/3")


def test_tmdb_requires_api_key(monkeypatch):
    monkeypatch.setattr("src.tmdb.load_dotenv", lambda: None)
    monkeypatch.delenv("TMDB_API_KEY", raising=False)

    with pytest.raises(APIError, match="TMDB API key is missing"):
        search_movies("Arrival")


def test_tmdb_handles_request_errors():
    session = FakeSession({})
    session.data = {}

    def broken_get(url, params, timeout):
        raise requests.exceptions.ConnectionError()

    session.get = broken_get

    with pytest.raises(APIError, match="temporarily unavailable"):
        search_movies("Arrival", api_key="test-key", session=session)
