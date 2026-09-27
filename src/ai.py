"""AI recommendation module for Group 17.

Responsibility: Ayebaebi Moses

Purpose:
- Use Gemini AI to provide personalized movie suggestions.
- Build a recommendation prompt from the user's preferences and saved movie context.
- Return movie suggestions and explanations that are useful to the user.

Expected flow:
1. Preferences and watchlist data are loaded.
2. A prompt is prepared with relevant user context.
3. Gemini is called with that prompt.
4. The response is formatted and shown in the UI.

Recommended functions:
- build_recommendation_prompt(preferences: list[str], watchlist: list[dict]) -> str
- get_ai_recommendations(preferences: list[str], watchlist: list[dict]) -> list[dict]
- format_ai_response(raw_response: str) -> list[dict]

Important notes:
- Keep prompts clear and specific.
- If the API call fails, show a friendly user-facing error.
- Do not expose raw API errors directly to the interface.
"""

# NOTE FOR TEAM:
# This module should rely on stored preferences and watchlist data.
# It should not own the user interface or file handling.
# The AI output should be easy to display in Streamlit cards or lists.
