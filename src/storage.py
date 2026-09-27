"""Local JSON storage layer for Group 17.

Responsibility: Baaz Habib

Purpose:
- Store preference, watchlist, and watched-movie data in JSON files.
- Read saved data safely and return it in a consistent Python structure.
- Handle missing files and invalid JSON without crashing the app.

Expected flow:
1. A feature saves data in Python dictionaries or lists.
2. This module writes the data to a local JSON file.
3. The UI or other modules load the data again when needed.

Recommended functions:
- ensure_storage_file(path: str) -> None
- read_json_file(path: str) -> dict | list
- write_json_file(path: str, data: dict | list) -> None

Important notes:
- Keep file names and paths consistent.
- Use safe read/write patterns.
- Do not expose raw file errors directly to the user; convert them to helpful messages.
"""

# NOTE FOR TEAM:
# This is the data layer of the app.
# It should not contain recommendation logic, UI code, or validation rules.
# It should simply manage JSON read/write operations reliably.
