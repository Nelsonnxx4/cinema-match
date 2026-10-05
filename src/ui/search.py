import streamlit as st

from src.errors import APIError, ValidationError
from src.tmdb import search_movies
from src.ui.components import render_movie_list, show_error


def render_search_page(api_key: str) -> None:
    st.subheader("Search Movies")

    with st.form("search_form"):
        movie_query = st.text_input("Movie title", placeholder="Search by title")
        submitted = st.form_submit_button("Search")

    if submitted and movie_query:
        if not api_key:
            st.warning("Add the movie API key in your .env file to search movies.")
        else:
            try:
                with st.spinner("Searching movies..."):
                    st.session_state["search_results"] = search_movies(
                        movie_query,
                        api_key=api_key,
                    )
            except (APIError, ValidationError) as error:
                show_error(error)

    render_movie_list(st.session_state["search_results"], "search")