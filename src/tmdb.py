"""TMDB API integration guide for Group 17.

Responsibility: Shalom Balogun

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
