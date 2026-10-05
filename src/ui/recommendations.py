import streamlit as st

from src.ai import get_ai_recommendations
from src.errors import APIError
from src.ui.components import show_error


def render_recommendations_page(
    saved_genres: list[str], watchlist: list[dict], api_key: str
) -> None:
    st.subheader("AI Recommendations")

    if st.button("Generate Recommendations"):
        if not api_key:
            st.warning("Add the AI API key in your .env file to generate recommendations.")
        else:
            try:
                with st.spinner("Generating recommendations..."):
                    st.session_state["ai_recommendations"] = get_ai_recommendations(
                        saved_genres,
                        watchlist,
                        api_key=api_key,
                    )
            except APIError as error:
                show_error(error)

    for recommendation in st.session_state["ai_recommendations"]:
        with st.container(border=True):
            st.subheader(recommendation["title"])
            st.write(recommendation["reason"])