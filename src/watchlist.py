"""Movie watchlist and watched-list module for Group 17.

Responsibility: Muhammad Hassan

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
