import json

import pytest

from src.errors import StorageError
from src.storage import ensure_storage_file, read_json_file, write_json_file


def test_ensure_storage_file_creates_missing_file(tmp_path):
    path = tmp_path / "watchlist.json"

    ensure_storage_file(str(path))

    assert json.loads(path.read_text()) == []


def test_ensure_storage_file_repairs_empty_file(tmp_path):
    path = tmp_path / "preference.json"
    path.write_text("")

    ensure_storage_file(str(path))

    assert json.loads(path.read_text()) == {"genres": []}


def test_ensure_storage_file_repairs_invalid_json(tmp_path):
    path = tmp_path / "watched.json"
    path.write_text("{broken json")

    ensure_storage_file(str(path))

    assert json.loads(path.read_text()) == []


def test_read_json_file_returns_saved_data(tmp_path):
    path = tmp_path / "watchlist.json"
    write_json_file(str(path), [{"id": 1, "title": "Inception"}])

    assert read_json_file(str(path)) == [{"id": 1, "title": "Inception"}]


def test_write_json_file_rejects_non_json_root_values(tmp_path):
    path = tmp_path / "watchlist.json"

    with pytest.raises(StorageError, match="Only dictionaries and lists"):
        write_json_file(str(path), "not valid")
