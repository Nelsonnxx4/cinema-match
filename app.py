from __future__ import annotations

import os

from dotenv import load_dotenv
import streamlit as st

from src.ai import get_ai_recommendations
from src.errors import APIError, StorageError, ValidationError, handle_validation_error
from src.preferences import clear_preferences, load_preferences, save_preferences
from src.tmdb import get_movie_details, get_movies_by_genres, search_movies
from src.validation import VALID_GENRES
from src.watchlist import (
    add_to_watchlist,
    get_watched_movies,
    get_watchlist,
    is_in_watchlist,
    mark_as_watched,
    remove_from_watchlist,
)


load_dotenv()

st.set_page_config(
    page_title="CinemaMatch",
    page_icon="CM",
    layout="wide",
)

def get_key(name: str, typed_value: str) -> str | None:
    if typed_value.strip():
        return typed_value.strip()

    env_value = os.getenv(name, "").strip()
    if env_value:
        return env_value

    return None


def show_message(error: Exception) -> None:
    if isinstance(error, ValidationError):
        st.error(handle_validation_error(str(error)))
    else:
        st.error(str(error))


def store_selected_movie(movie: dict) -> None:
    st.session_state["selected_movie_id"] = movie.get("id")
    st.session_state["selected_movie_summary"] = movie


def render_genres(genres: list[str]) -> None:
    if not genres:
        return

    st.caption("Genres: " + ", ".join(genres))


def render_movie_card(
    movie: dict,
    key_prefix: str,
    show_remove: bool = False,
    show_watched: bool = True,
) -> None:
    movie_id = movie.get("id")

    with st.container(border=True):
        poster_column, content_column = st.columns([1, 4], gap="medium")

        with poster_column:
            poster_url = movie.get("poster_url")
            if poster_url:
                st.image(poster_url, width="stretch")
            else:
                st.write("No poster")

        with content_column:
            title = movie.get("title", "Untitled")
            year = movie.get("year")
            rating = movie.get("rating", 0)
            st.subheader(f"{title} ({year})" if year else title)
            st.caption(f"Rating: {float(rating):.1f}" if rating else "Rating unavailable")
            render_genres(movie.get("genres", []))

            overview = movie.get("overview")
            if overview:
                st.write(overview)
            else:
                st.write("No overview available.")

            details_column, save_column, watched_column, remove_column = st.columns(4)

            with details_column:
                if st.button("Details", key=f"{key_prefix}_details_{movie_id}"):
                    store_selected_movie(movie)
                    st.rerun()

            with save_column:
                already_saved = bool(movie_id) and is_in_watchlist(movie_id)
                if already_saved and not show_remove:
                    st.button("Saved", key=f"{key_prefix}_saved_{movie_id}", disabled=True)
                else:
                    if st.button("Watchlist", key=f"{key_prefix}_save_{movie_id}"):
                        add_to_watchlist(movie)
                        st.success("Saved to watchlist.")
                        st.rerun()

            with watched_column:
                if show_watched and st.button("Watched", key=f"{key_prefix}_watched_{movie_id}"):
                    mark_as_watched(movie)
                    st.success("Marked as watched.")
                    st.rerun()

            with remove_column:
                if show_remove and st.button("Remove", key=f"{key_prefix}_remove_{movie_id}"):
                    remove_from_watchlist(movie_id)
                    st.success("Removed from watchlist.")
                    st.rerun()


def render_results(movies: list[dict], key_prefix: str) -> None:
    if not movies:
        st.info("No movies to show.")
        return

    for movie in movies:
        render_movie_card(movie, key_prefix)


def render_discover_tab(tmdb_api_key: str | None) -> None:
    try:
        saved_preferences = load_preferences()
    except (StorageError, ValidationError) as error:
        saved_preferences = []
        show_message(error)

    with st.form("discover_form"):
        selected_genres = st.multiselect(
            "Genres",
            options=list(VALID_GENRES),
            default=saved_preferences,
        )

        save_column, discover_column, clear_column = st.columns([1, 1, 1])
        save_clicked = save_column.form_submit_button("Save preferences")
        discover_clicked = discover_column.form_submit_button("Discover movies", type="primary")
        clear_clicked = clear_column.form_submit_button("Clear preferences")

    if clear_clicked:
        try:
            clear_preferences()
            st.session_state["discover_results"] = []
            st.success("Preferences cleared.")
            st.rerun()
        except StorageError as error:
            show_message(error)

    if save_clicked or discover_clicked:
        try:
            save_preferences(selected_genres)
            st.success("Preferences saved.")
        except (StorageError, ValidationError) as error:
            show_message(error)
            return

    if discover_clicked:
        if not tmdb_api_key:
            st.warning("Add a TMDB API key to discover movies.")
            return

        try:
            with st.spinner("Loading movies..."):
                st.session_state["discover_results"] = get_movies_by_genres(
                    selected_genres,
                    api_key=tmdb_api_key,
                )
        except (APIError, ValidationError) as error:
            show_message(error)

    render_results(st.session_state.get("discover_results", []), "discover")


def render_search_tab(tmdb_api_key: str | None) -> None:
    with st.form("search_form"):
        query = st.text_input("Movie title", placeholder="Search by title")
        search_clicked = st.form_submit_button("Search", type="primary")

    if search_clicked:
        if not tmdb_api_key:
            st.warning("Add a TMDB API key to search movies.")
            return

        try:
            with st.spinner("Searching movies..."):
                st.session_state["search_results"] = search_movies(
                    query,
                    api_key=tmdb_api_key,
                )
        except (APIError, ValidationError) as error:
            show_message(error)

    render_results(st.session_state.get("search_results", []), "search")


def render_watchlist_tab() -> None:
    try:
        watchlist = get_watchlist()
        watched_movies = get_watched_movies()
    except (StorageError, ValidationError) as error:
        show_message(error)
        return

    watchlist_tab, watched_tab = st.tabs(["Watchlist", "Watched"])

    with watchlist_tab:
        if not watchlist:
            st.info("Your watchlist is empty.")
        for movie in watchlist:
            render_movie_card(
                movie,
                "watchlist",
                show_remove=True,
                show_watched=True,
            )

    with watched_tab:
        if not watched_movies:
            st.info("No watched movies yet.")
        for movie in watched_movies:
            with st.container(border=True):
                title = movie.get("title", "Untitled")
                year = movie.get("year")
                st.subheader(f"{title} ({year})" if year else title)
                render_genres(movie.get("genres", []))
                st.write(movie.get("overview") or "No overview available.")
                if st.button("Add back to watchlist", key=f"restore_{movie.get('id')}"):
                    add_to_watchlist(movie)
                    st.success("Added back to watchlist.")
                    st.rerun()


def render_recommendations_tab(gemini_api_key: str | None) -> None:
    try:
        preferences = load_preferences()
        watchlist = get_watchlist()
    except (StorageError, ValidationError) as error:
        show_message(error)
        return

    metric_columns = st.columns(2)
    metric_columns[0].metric("Saved genres", len(preferences))
    metric_columns[1].metric("Watchlist movies", len(watchlist))

    if st.button("Generate recommendations", type="primary"):
        if not gemini_api_key:
            st.warning("Add a Gemini API key to generate recommendations.")
            return

        try:
            with st.spinner("Generating recommendations..."):
                st.session_state["ai_recommendations"] = get_ai_recommendations(
                    preferences,
                    watchlist,
                    api_key=gemini_api_key,
                )
        except APIError as error:
            show_message(error)

    recommendations = st.session_state.get("ai_recommendations", [])
    for recommendation in recommendations:
        with st.container(border=True):
            st.subheader(recommendation["title"])
            st.write(recommendation["reason"])


def render_selected_movie_details(tmdb_api_key: str | None) -> None:
    movie_id = st.session_state.get("selected_movie_id")
    summary = st.session_state.get("selected_movie_summary")

    if not movie_id or not summary:
        return

    st.divider()
    st.header("Movie Details")

    details = summary
    if tmdb_api_key:
        try:
            with st.spinner("Loading details..."):
                details = get_movie_details(movie_id, api_key=tmdb_api_key)
        except APIError as error:
            st.warning(str(error))

    left_column, right_column = st.columns([1, 3], gap="large")
    with left_column:
        poster_url = details.get("poster_url")
        if poster_url:
            st.image(poster_url, width="stretch")
        else:
            st.write("No poster")

    with right_column:
        title = details.get("title", "Untitled")
        year = details.get("year")
        runtime = details.get("runtime")
        rating = details.get("rating", 0)

        st.subheader(f"{title} ({year})" if year else title)
        detail_bits = []
        if runtime:
            detail_bits.append(f"{runtime} min")
        if rating:
            detail_bits.append(f"{float(rating):.1f} rating")
        if detail_bits:
            st.caption(" | ".join(detail_bits))

        render_genres(details.get("genres", []))
        st.write(details.get("overview") or "No overview available.")

        action_columns = st.columns(3)
        if action_columns[0].button("Add to watchlist", key=f"details_save_{movie_id}"):
            add_to_watchlist(details)
            st.success("Saved to watchlist.")
            st.rerun()
        if action_columns[1].button("Mark watched", key=f"details_watched_{movie_id}"):
            mark_as_watched(details)
            st.success("Marked as watched.")
            st.rerun()
        if action_columns[2].button("Close details", key=f"details_close_{movie_id}"):
            st.session_state.pop("selected_movie_id", None)
            st.session_state.pop("selected_movie_summary", None)
            st.rerun()

        tmdb_url = details.get("tmdb_url")
        homepage = details.get("homepage")
        if tmdb_url:
            st.link_button("Open on TMDB", tmdb_url)
        if homepage:
            st.link_button("Official site", homepage)


def main() -> None:
    st.session_state.setdefault("discover_results", [])
    st.session_state.setdefault("search_results", [])
    st.session_state.setdefault("ai_recommendations", [])

    with st.sidebar:
        st.header("Settings")
        tmdb_input = st.text_input(
            "TMDB API key",
            type="password",
            placeholder="Uses .env when empty",
        )
        gemini_input = st.text_input(
            "Gemini API key",
            type="password",
            placeholder="Uses .env when empty",
        )

        tmdb_api_key = get_key("TMDB_API_KEY", tmdb_input)
        gemini_api_key = get_key("GEMINI_API_KEY", gemini_input) or get_key(
            "GOOGLE_API_KEY",
            "",
        )

        st.divider()
        st.caption(f"TMDB: {'ready' if tmdb_api_key else 'missing'}")
        st.caption(f"Gemini: {'ready' if gemini_api_key else 'missing'}")

    st.title("CinemaMatch")

    try:
        watchlist_count = len(get_watchlist())
        watched_count = len(get_watched_movies())
        preference_count = len(load_preferences())
    except (StorageError, ValidationError):
        watchlist_count = 0
        watched_count = 0
        preference_count = 0

    stat_columns = st.columns(3)
    stat_columns[0].metric("Saved genres", preference_count)
    stat_columns[1].metric("Watchlist", watchlist_count)
    stat_columns[2].metric("Watched", watched_count)

    discover_tab, search_tab, watchlist_tab, recommendations_tab = st.tabs(
        ["Discover", "Search", "Watchlist", "AI Recommendations"]
    )

    with discover_tab:
        render_discover_tab(tmdb_api_key)

    with search_tab:
        render_search_tab(tmdb_api_key)

    with watchlist_tab:
        render_watchlist_tab()

    with recommendations_tab:
        render_recommendations_tab(gemini_api_key)

    render_selected_movie_details(tmdb_api_key)


if __name__ == "__main__":
    main()
