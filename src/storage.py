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

from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
from typing import Any

from src.errors import StorageError, handle_file_error


JsonData = dict[str, Any] | list[Any]

DEFAULT_DATA_BY_FILE = {
    "preference.json": {"genres": []},
    "watchlist.json": [],
    "watched.json": [],
}


def get_default_data(path: str) -> JsonData:
    """Return the default JSON shape for a known storage file."""
    file_name = Path(path).name
    return deepcopy(DEFAULT_DATA_BY_FILE.get(file_name, {}))


def ensure_storage_file(path: str, default_data: JsonData | None = None) -> None:
    """Create a JSON storage file if it is missing, empty, or invalid."""
    storage_path = Path(path)
    data_to_write = default_data if default_data is not None else get_default_data(path)

    try:
        storage_path.parent.mkdir(parents=True, exist_ok=True)

        if not storage_path.exists() or storage_path.stat().st_size == 0:
            write_json_file(path, data_to_write)
            return

        with storage_path.open("r", encoding="utf-8") as file:
            saved_data = json.load(file)

        if not isinstance(saved_data, (dict, list)):
            write_json_file(path, data_to_write)
    except json.JSONDecodeError:
        write_json_file(path, data_to_write)
    except OSError as error:
        raise StorageError(handle_file_error(error)) from error


def read_json_file(path: str, default_data: JsonData | None = None) -> JsonData:
    """Read JSON data safely from a local file."""
    ensure_storage_file(path, default_data)

    try:
        with Path(path).open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise StorageError(handle_file_error(error)) from error
    except OSError as error:
        raise StorageError(handle_file_error(error)) from error

    if not isinstance(data, (dict, list)):
        raise StorageError("Saved data must be a JSON object or list.")

    return data


def write_json_file(path: str, data: JsonData) -> None:
    """Write dictionaries or lists to a JSON file."""
    if not isinstance(data, (dict, list)):
        raise StorageError("Only dictionaries and lists can be saved as JSON.")

    storage_path = Path(path)
    temporary_path = storage_path.with_suffix(storage_path.suffix + ".tmp")

    try:
        storage_path.parent.mkdir(parents=True, exist_ok=True)

        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
            file.write("\n")

        os.replace(temporary_path, storage_path)
    except OSError as error:
        raise StorageError(handle_file_error(error)) from error
