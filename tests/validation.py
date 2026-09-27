"""Validation tests for Group 17.

Purpose:
- Verify that user input cleaning works as expected.
- Ensure invalid values are rejected before they reach the app logic.
- Protect the validation module from regressions.

Suggested tests:
- clean_text removes unwanted spaces and weird formatting
- validate_genre accepts valid genre names
- validate_genre rejects empty or invalid values
- normalize_genre_list removes duplicates and empty values

Important notes:
- Write tests for real behavior, not just mock output.
- Keep tests simple and readable.
- Use pytest for all validation checks.
"""

# NOTE FOR TEAM:
# If validation is changed, tests must be updated as well.
# This file is meant to guarantee that input handling remains stable
# across the entire application.
