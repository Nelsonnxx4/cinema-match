import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT / "src"))

from src.ai import get_ai_recommendations
from src.errors import APIError, StorageError, ValidationError, handle_validation_error
from src.preferences import clear_preferences, load_preferences, save_preferences
from src.tmdb import get_movie_details, get_movies_by_genres, search_movies
from src.watchlist import (
    add_to_watchlist,
    get_watched_movies,
    get_watchlist,
    is_in_watchlist,
    mark_as_watched,
    remove_from_watchlist,
)

try:
    from src.validation import VALID_GENRES
except ImportError:
    VALID_GENRES = (
        "Action",
        "Adventure",
        "Animation",
        "Comedy",
        "Crime",
        "Documentary",
        "Drama",
        "Family",
        "Fantasy",
        "History",
        "Horror",
        "Music",
        "Mystery",
        "Romance",
        "Science Fiction",
        "TV Movie",
        "Thriller",
        "War",
        "Western",
    )


# 1. Page Configuration

load_dotenv()
st.set_page_config(page_title="CinemaMatch", page_icon="CM", layout="wide")

PAGES = ["Discover", "Search", "Preferences", "Watchlist", "AI Recommendations"]
tmdb_api_key = os.getenv("TMDB_API_KEY", "").strip()
gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv(
    "GOOGLE_API_KEY",
    "",
).strip()


# 2. Helper Functions

def show_error(error: Exception) -> None:
    message = handle_validation_error(str(error)) if isinstance(error, ValidationError) else str(error)
    st.error(message)


def load_app_data() -> tuple[list[str], list[dict], list[dict]]:
    try:
        return load_preferences(), get_watchlist(), get_watched_movies()
    except Exception:
        return [], [], []


def run_action(action, success_message: str) -> None:
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
                st.image(movie["poster_url"], use_container_width=True)
            else:
                st.write("No poster")

        with info_col:
            st.subheader(f"{title} ({year})" if year else title)
            st.caption(f"Rating: {float(rating):.1f}" if rating else "Rating unavailable")
            show_genres(movie.get("genres", []))
            st.write(movie.get("overview") or "No overview available.")

            b1, b2, b3, b4 = st.columns(4)
            if b1.button("Details", key=f"{key}_details_{movie_id}"):
                st.session_state["selected_movie"] = movie

            if movie_id and is_in_watchlist(movie_id) and not allow_remove:
                b2.button("Saved", key=f"{key}_saved_{movie_id}", disabled=True)
            elif b2.button("Watchlist", key=f"{key}_watchlist_{movie_id}"):
                run_action(lambda: add_to_watchlist(movie), "Saved to watchlist.")

            if b3.button("Watched", key=f"{key}_watched_{movie_id}"):
                run_action(lambda: mark_as_watched(movie), "Marked as watched.")

            if allow_remove and b4.button("Remove", key=f"{key}_remove_{movie_id}"):
                run_action(lambda: remove_from_watchlist(movie_id), "Removed from watchlist.")


def render_movie_list(movies: list[dict], key: str, allow_remove: bool = False) -> None:
    if not movies:
        st.info("No movies to show.")
        return

    for movie in movies:
        show_movie(movie, key, allow_remove)


def preference_form(form_key: str, saved_genres: list[str], columns: int = 2):
    with st.form(form_key):
        selected_genres = st.multiselect(
            "Genres",
            options=list(VALID_GENRES),
            default=saved_genres,
        )
        cols = st.columns(columns)
        save_clicked = cols[0].form_submit_button("Save Preferences")
        clear_clicked = cols[-1].form_submit_button("Clear")
    return selected_genres, save_clicked, clear_clicked


# 3. Session State and Sidebar

for key, default in {
    "page": "Discover",
    "discover_results": [],
    "search_results": [],
    "ai_recommendations": [],
}.items():
    st.session_state.setdefault(key, default)

with st.sidebar:
    st.header("Menu")
    for page in PAGES:
        button_type = "primary" if st.session_state["page"] == page else "secondary"
        if st.button(page, type=button_type, use_container_width=True):
            st.session_state["page"] = page
            st.rerun()


# 4. Header and Summary

saved_genres, watchlist, watched_movies = load_app_data()

st.title("CinemaMatch")
m1, m2, m3 = st.columns(3)
m1.metric("Saved Genres", len(saved_genres))
m2.metric("Watchlist", len(watchlist))
m3.metric("Watched", len(watched_movies))


# 5. Discover Movies

if st.session_state["page"] == "Discover":
    st.subheader("Discover Movies")

    with st.form("discover_form"):
        selected_genres = st.multiselect(
            "Genres",
            options=list(VALID_GENRES),
            default=saved_genres,
        )
        c1, c2, c3 = st.columns(3)
        save_clicked = c1.form_submit_button("Save Preferences")
        discover_clicked = c2.form_submit_button("Discover Movies")
        clear_clicked = c3.form_submit_button("Clear")

    if clear_clicked:
        run_action(
            lambda: (clear_preferences(), st.session_state.update(discover_results=[])),
            "Preferences cleared.",
        )

    if save_clicked:
        run_action(lambda: save_preferences(selected_genres), "Preferences saved.")

    if discover_clicked:
        if not tmdb_api_key:
            st.warning("Add the movie API key in your .env file to discover movies.")
        else:
            try:
                save_preferences(selected_genres)
                with st.spinner("Loading movies..."):
                    st.session_state["discover_results"] = get_movies_by_genres(
                        selected_genres,
                        api_key=tmdb_api_key,
                    )
            except (APIError, StorageError, ValidationError) as error:
                show_error(error)

    render_movie_list(st.session_state["discover_results"], "discover")


# 6. Search Movies

elif st.session_state["page"] == "Search":
    st.subheader("Search Movies")

    with st.form("search_form"):
        movie_query = st.text_input("Movie title", placeholder="Search by title")
        submitted = st.form_submit_button("Search")

    if submitted and movie_query:
        if not tmdb_api_key:
            st.warning("Add the movie API key in your .env file to search movies.")
        else:
            try:
                with st.spinner("Searching movies..."):
                    st.session_state["search_results"] = search_movies(
                        movie_query,
                        api_key=tmdb_api_key,
                    )
            except (APIError, ValidationError) as error:
                show_error(error)

    render_movie_list(st.session_state["search_results"], "search")


# 7. Preferences

elif st.session_state["page"] == "Preferences":
    st.subheader("Preferences")
    selected_genres, save_clicked, clear_clicked = preference_form(
        "preferences_form",
        saved_genres,
    )

    if save_clicked:
        run_action(lambda: save_preferences(selected_genres), "Preferences saved.")
    if clear_clicked:
        run_action(clear_preferences, "Preferences cleared.")


# 8. Watchlist and Watched Movies

elif st.session_state["page"] == "Watchlist":
    st.subheader("Watchlist")
    watchlist_tab, watched_tab = st.tabs(["Watchlist", "Watched"])

    with watchlist_tab:
        render_movie_list(watchlist, "watchlist", allow_remove=True)

    with watched_tab:
        if not watched_movies:
            st.info("No watched movies yet.")
        for movie in watched_movies:
            with st.container(border=True):
                st.subheader(movie.get("title", "Untitled"))
                show_genres(movie.get("genres", []))
                st.write(movie.get("overview") or "No overview available.")
                if st.button("Add Back to Watchlist", key=f"restore_{movie.get('id')}"):
                    run_action(lambda movie=movie: add_to_watchlist(movie), "Added back to watchlist.")


# 9. AI Recommendations

elif st.session_state["page"] == "AI Recommendations":
    st.subheader("AI Recommendations")

    if st.button("Generate Recommendations"):
        if not gemini_api_key:
            st.warning("Add the AI API key in your .env file to generate recommendations.")
        else:
            try:
                with st.spinner("Generating recommendations..."):
                    st.session_state["ai_recommendations"] = get_ai_recommendations(
                        saved_genres,
                        watchlist,
                        api_key=gemini_api_key,
                    )
            except APIError as error:
                show_error(error)

    for recommendation in st.session_state["ai_recommendations"]:
        with st.container(border=True):
            st.subheader(recommendation["title"])
            st.write(recommendation["reason"])


# 10. Selected Movie Details

selected_movie = st.session_state.get("selected_movie")

if selected_movie:
    movie_id = selected_movie.get("id")
    details = selected_movie

    if tmdb_api_key and movie_id:
        try:
            details = get_movie_details(movie_id, api_key=tmdb_api_key)
        except APIError:
            details = selected_movie

    st.divider()
    st.header("Movie Details")

    poster_col, info_col = st.columns([1, 3])
    with poster_col:
        if details.get("poster_url"):
            st.image(details["poster_url"], use_container_width=True)

    with info_col:
        st.subheader(details.get("title", "Untitled"))
        show_genres(details.get("genres", []))
        st.write(details.get("overview") or "No overview available.")

        b1, b2, b3 = st.columns(3)
        if b1.button("Add to Watchlist"):
            run_action(lambda: add_to_watchlist(details), "Saved to watchlist.")
        if b2.button("Mark Watched"):
            run_action(lambda: mark_as_watched(details), "Marked as watched.")
        if b3.button("Close Details"):
            st.session_state.pop("selected_movie", None)
            st.rerun()
