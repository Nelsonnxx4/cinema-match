import streamlit as st

from src.ui.components import render_movie_list, run_action, show_genres
from src.watchlist import add_to_watchlist


def render_watchlist_page(
    watchlist: list[dict], watched_movies: list[dict]
) -> None:
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
                    run_action(
                        lambda movie=movie: add_to_watchlist(movie),
                        "Added back to watchlist.",
                    )