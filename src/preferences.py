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

Recommended functions:
- save_preferences(genres: list[str]) -> None
- load_preferences() -> list[str]
- update_preferences(new_genres: list[str]) -> list[str]

Important notes:
- Prefer a clean JSON-friendly structure.
- Avoid duplicate genres.
- Make sure AI and UI layers read the same preference format.
"""

# NOTE FOR TEAM:
# This module owns the user preference state.
# Keep the schema stable so other modules do not break when reading saved data.
# A preference should be simple: a list of genres or a JSON object with genres.
