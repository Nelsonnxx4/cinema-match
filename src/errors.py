"""Centralized error handling for CinemaMatch.

This module defines app-specific exceptions and converts technical errors into
user-friendly messages.
"""

from __future__ import annotations

import json


class CinemaMatchError(Exception):
  pass

class ValidationError(CinemaMatchError):
  pass

class APIError(CinemaMatchError):
  pass


class StorageError(CinemaMatchError):
  pass

def handle_api_error(error: Exception) -> str:
    if isinstance(error, TimeoutError):
        return "The movie service is taking too long. Please try again."
    if isinstance(error, ConnectionError):
        return "The movie service is temporarily unavailable."
    return "We couldn't load movie data right now. Please try again later."


def handle_file_error(error: Exception) -> str:
    if isinstance(error, FileNotFoundError):
        return "Saved data could not be found. A new file will be created."
    if isinstance(error, json.JSONDecodeError):
        return "Saved data is damaged and needs to be reset."
    return "There was a problem reading your saved data."


def handle_validation_error(message: str) -> str:
    return f"Invalid input: {message}"
