import pytest

from src.errors import StorageError, ValidationError
from src.preferences import (
    clear_preferences,
    load_preferences,
    save_preferences,
    update_preferences,
)
from src.storage import write_json_file


def test_save_preferences_stores_normalized_genres(tmp_path):
    path = tmp_path / "preference.json"

    save_preferences([" action ", "Comedy", "action"], str(path))

    assert load_preferences(str(path)) == ["Action", "Comedy"]


def test_load_preferences_returns_empty_list_for_new_file(tmp_path):
    path = tmp_path / "preference.json"

    assert load_preferences(str(path)) == []


def test_load_preferences_supports_old_list_format(tmp_path):
    path = tmp_path / "preference.json"
    write_json_file(str(path), ["drama", "Drama", "Thriller"])

    assert load_preferences(str(path)) == ["Drama", "Thriller"]


def test_update_preferences_adds_new_unique_genres(tmp_path):
    path = tmp_path / "preference.json"
    save_preferences(["Action"], str(path))

    updated_genres = update_preferences(["Comedy", "action"], str(path))

    assert updated_genres == ["Action", "Comedy"]
    assert load_preferences(str(path)) == ["Action", "Comedy"]


def test_clear_preferences_resets_saved_genres(tmp_path):
    path = tmp_path / "preference.json"
    save_preferences(["Action"], str(path))

    clear_preferences(str(path))

    assert load_preferences(str(path)) == []


def test_save_preferences_rejects_unknown_genres(tmp_path):
    path = tmp_path / "preference.json"

    with pytest.raises(ValidationError, match="unsupported genre"):
        save_preferences(["Action", "Space Opera"], str(path))


def test_load_preferences_rejects_invalid_schema(tmp_path):
    path = tmp_path / "preference.json"
    write_json_file(str(path), {"genres": "Action"})

    with pytest.raises(StorageError, match="Preference genres"):
        load_preferences(str(path))
