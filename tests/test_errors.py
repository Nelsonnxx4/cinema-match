from src.errors import (
    APIError,
    CinemaMatchError,
    StorageError,
    ValidationError,
    handle_api_error,
    handle_file_error,
    handle_validation_error,
)


def test_custom_exceptions_are_app_specific():
    assert issubclass(ValidationError, CinemaMatchError)
    assert issubclass(APIError, CinemaMatchError)
    assert issubclass(StorageError, CinemaMatchError)


def test_validation_error_message_is_user_friendly():
    assert handle_validation_error("genre is required") == "Invalid input: genre is required"


def test_api_error_message_for_timeout():
    assert handle_api_error(TimeoutError()) == "The movie service is taking too long. Please try again."


def test_file_error_message_for_missing_file():
    assert handle_file_error(FileNotFoundError()) == "Saved data could not be found. A new file will be created."
