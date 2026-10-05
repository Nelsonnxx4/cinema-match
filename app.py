import os

import streamlit as st
from dotenv import load_dotenv

from src.preferences import load_preferences
from src.ui.details import render_selected_movie_details
from src.ui.discover import render_discover_page
from src.ui.preferences import render_preferences_page
from src.ui.recommendations import render_recommendations_page
from src.ui.search import render_search_page
from src.ui.watchlist import render_watchlist_page
from src.watchlist import get_watched_movies, get_watchlist


PAGES = ("Discover", "Search", "Preferences", "Watchlist", "AI Recommendations")


def load_app_data() -> tuple[list[str], list[dict], list[dict]]:
    try:
        return load_preferences(), get_watchlist(), get_watched_movies()
    except Exception:
        return [], [], []


def main() -> None:
    load_dotenv()
    st.set_page_config(page_title="CinemaMatch", page_icon="CM", layout="wide")

    tmdb_api_key = os.getenv("TMDB_API_KEY", "").strip()
    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv(
        "GOOGLE_API_KEY", ""
    ).strip()

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

    saved_genres, watchlist, watched_movies = load_app_data()

    st.title("CinemaMatch🎥")
    metrics = st.columns(3)
    metrics[0].metric("Saved Genres", len(saved_genres))
    metrics[1].metric("Watchlist", len(watchlist))
    metrics[2].metric("Watched", len(watched_movies))

    page = st.session_state["page"]
    if page == "Discover":
        render_discover_page(saved_genres, tmdb_api_key)
    elif page == "Search":
        render_search_page(tmdb_api_key)
    elif page == "Preferences":
        render_preferences_page(saved_genres)
    elif page == "Watchlist":
        render_watchlist_page(watchlist, watched_movies)
    elif page == "AI Recommendations":
        render_recommendations_page(saved_genres, watchlist, gemini_api_key)

    render_selected_movie_details(tmdb_api_key)


if __name__ == "__main__":
    main()
