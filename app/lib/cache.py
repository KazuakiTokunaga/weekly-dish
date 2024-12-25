import pandas as pd
import streamlit as st

from lib.recipe import get_ingredients_data, get_menu_data, get_recent_menu
from lib.util import Menu


@st.cache_data
def fetch_menu_data() -> list[Menu]:
    """Fetch menu data once per session."""
    return get_menu_data()


@st.cache_data
def fetch_ingredients_data() -> pd.DataFrame:
    """Fetch ingredients data once per session."""
    return get_ingredients_data()


@st.cache_data
def fetch_recent_menu_list() -> tuple[list[str], list[str]]:
    """Fetch recent menu data once per session."""
    return get_recent_menu()
