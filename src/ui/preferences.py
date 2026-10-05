import streamlit as st

from src.preferences import clear_preferences, save_preferences
from src.ui.components import preference_form, run_action


def render_preferences_page(saved_genres: list[str]) -> None:
    st.subheader("Preferences")
    selected_genres, save_clicked, clear_clicked = preference_form(
        "preferences_form",
        saved_genres,
    )

    if save_clicked:
        run_action(lambda: save_preferences(selected_genres), "Preferences saved.")
    if clear_clicked:
        run_action(clear_preferences, "Preferences cleared.")