import streamlit as st

from src.errors import APIError
from src.tmdb import get_movie_details
from src.ui.components import run_action, show_genres
from src.watchlist import add_to_watchlist, mark_as_watched


def render_selected_movie_details(api_key: str) -> None:
    selected_movie = st.session_state.get("selected_movie")
    if not selected_movie:
        return

    movie_id = selected_movie.get("id")
    details = selected_movie
    if api_key and movie_id:
        try:
            details = get_movie_details(movie_id, api_key=api_key)
        except APIError:
            details = selected_movie

    st.divider()
    st.header("Movie Details")
    poster_column, info_column = st.columns([1, 3])

    with poster_column:
        if details.get("poster_url"):
            st.image(details["poster_url"], width="stretch")

    with info_column:
        st.subheader(details.get("title", "Untitled"))
        show_genres(details.get("genres", []))
        st.write(details.get("overview") or "No overview available.")

        add_button, watched_button, close_button = st.columns(3)
        if add_button.button("Add to Watchlist"):
            run_action(lambda: add_to_watchlist(details), "Saved to watchlist.")
        if watched_button.button("Mark Watched"):
            run_action(lambda: mark_as_watched(details), "Marked as watched.")
        if close_button.button("Close Details"):
            st.session_state.pop("selected_movie", None)
            st.rerun()