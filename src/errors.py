"""Error handling utilities for Group 17.

Responsibility: Oryiman Orhembetyoga

Purpose:
- Handle API failures, invalid user input, missing files, and network issues.
- Prevent the app from crashing during runtime.
- Return user-friendly messages and safe fallback behavior.

Expected flow:
1. A module raises or catches a problem.
2. This layer converts the issue into a clear message.
3. The UI can inform the user without breaking the flow.

Recommended functions:
- handle_api_error(error: Exception) -> str
- handle_file_error(error: Exception) -> str
- handle_validation_error(message: str) -> str

Important notes:
- Error handling must be consistent across the app.
- Keep messages understandable to non-technical users.
- Prefer graceful fallback behavior over terminal exceptions.
"""

# NOTE FOR TEAM:
# This module is not a feature by itself; it supports the whole app.
# Every feature should use it when a request, file, or API call may fail.
