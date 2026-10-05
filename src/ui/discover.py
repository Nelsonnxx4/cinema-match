import streamlit as st

from src.errors import APIError, StorageError, ValidationError
from src.preferences import clear_preferences, save_preferences
from src.tmdb import get_movies_by_genres
from src.ui.components import render_movie_list, run_action, show_error
from src.validation import VALID_GENRES


def render_discover_page(saved_genres: list[str], api_key: str) -> None:
    st.subheader("Discover Movies")

    with st.form("discover_form"):
        selected_genres = st.multiselect(
            "Genres",
            options=list(VALID_GENRES),
            default=saved_genres,
        )
        save_column, discover_column, clear_column = st.columns(3)
        save_clicked = save_column.form_submit_button("Save Preferences")
        discover_clicked = discover_column.form_submit_button("Discover Movies")
        clear_clicked = clear_column.form_submit_button("Clear")

    if clear_clicked:
        run_action(
            lambda: (clear_preferences(), st.session_state.update(discover_results=[])),
            "Preferences cleared.",
        )

    if save_clicked:
        run_action(lambda: save_preferences(selected_genres), "Preferences saved.")

    if discover_clicked:
        if not api_key:
            st.warning("Add the movie API key in your .env file to discover movies.")
        else:
            try:
                save_preferences(selected_genres)
                with st.spinner("Loading movies..."):
                    st.session_state["discover_results"] = get_movies_by_genres(
                        selected_genres,
                        api_key=api_key,
                    )
            except (APIError, StorageError, ValidationError) as error:
                show_error(error)

    render_movie_list(st.session_state["discover_results"], "discover")