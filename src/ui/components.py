from collections.abc import Callable

import streamlit as st

from src.errors import APIError, StorageError, ValidationError, handle_validation_error
from src.validation import VALID_GENRES
from src.watchlist import (
    add_to_watchlist,
    is_in_watchlist,
    mark_as_watched,
    remove_from_watchlist,
)


def show_error(error: Exception) -> None:
    message = (
        handle_validation_error(str(error))
        if isinstance(error, ValidationError)
        else str(error)
    )
    st.error(message)


def run_action(action: Callable[[], object], success_message: str) -> None:
    try:
        action()
        st.success(success_message)
        st.rerun()
    except (APIError, StorageError, ValidationError) as error:
        show_error(error)


def show_genres(genres: list[str]) -> None:
    if genres:
        st.caption("Genres: " + ", ".join(genres))


def show_movie(movie: dict, key: str, allow_remove: bool = False) -> None:
    movie_id = movie.get("id")
    title = movie.get("title", "Untitled")
    year = movie.get("year")
    rating = movie.get("rating", 0)

    with st.container(border=True):
        poster_col, info_col = st.columns([1, 4])

        with poster_col:
            if movie.get("poster_url"):
                st.image(movie["poster_url"], width="stretch")
            else:
                st.write("No poster")

        with info_col:
            st.subheader(f"{title} ({year})" if year else title)
            st.caption(
                f"Rating: {float(rating):.1f}" if rating else "Rating unavailable"
            )
            show_genres(movie.get("genres", []))
            st.write(movie.get("overview") or "No overview available.")

            details_button, watchlist_button, watched_button, remove_button = st.columns(4)
            if details_button.button("Details", key=f"{key}_details_{movie_id}"):
                st.session_state["selected_movie"] = movie

            if movie_id and is_in_watchlist(movie_id) and not allow_remove:
                watchlist_button.button(
                    "Saved", key=f"{key}_saved_{movie_id}", disabled=True
                )
            elif watchlist_button.button(
                "Watchlist", key=f"{key}_watchlist_{movie_id}"
            ):
                run_action(lambda: add_to_watchlist(movie), "Saved to watchlist.")

            if watched_button.button("Watched", key=f"{key}_watched_{movie_id}"):
                run_action(lambda: mark_as_watched(movie), "Marked as watched.")

            if allow_remove and remove_button.button(
                "Remove", key=f"{key}_remove_{movie_id}"
            ):
                run_action(
                    lambda: remove_from_watchlist(movie_id), "Removed from watchlist."
                )


def render_movie_list(
    movies: list[dict], key: str, allow_remove: bool = False
) -> None:
    if not movies:
        st.info("No movies to show.")
        return

    for movie in movies:
        show_movie(movie, key, allow_remove)


def preference_form(
    form_key: str, saved_genres: list[str], columns: int = 2
) -> tuple[list[str], bool, bool]:
    with st.form(form_key):
        selected_genres = st.multiselect(
            "Genres",
            options=list(VALID_GENRES),
            default=saved_genres,
        )
        form_columns = st.columns(columns)
        save_clicked = form_columns[0].form_submit_button("Save Preferences")
        clear_clicked = form_columns[-1].form_submit_button("Clear")
    return selected_genres, save_clicked, clear_clicked