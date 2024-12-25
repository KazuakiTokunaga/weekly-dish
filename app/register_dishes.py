from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from lib.recipe import get_menu_data, get_recent_menu, register_dish_history
from lib.util import Menu

# Title and header
st.title("食べた主菜を登録")


@st.cache_data
def fetch_menu_data():
    """Fetch menu data once per session."""
    return get_menu_data()


@st.cache_data
def get_recent_menu_list():
    """Fetch recent menu data once per session."""
    return get_recent_menu()


def generate_recent_dates():
    today = datetime.now(ZoneInfo("Asia/Tokyo"))
    return [today - timedelta(days=i) for i in range(3)]


# Load menu data
dishes: list[Menu] = fetch_menu_data()
dish_list = [dish.name for dish in dishes]
recent_menu_list, date_list = get_recent_menu_list()

# Generate recent dates
dates = generate_recent_dates()

# Session state to retain user input
if "day_to_register_dish" not in st.session_state:
    st.session_state.day_to_register_dish = {date.strftime("%Y-%m-%d"): "" for date in dates}
    st.session_state.dates = {date.strftime("%Y-%m-%d"): date for date in dates}

# Form to register dishes
with st.form(key="dish_registration_form"):
    for date_key in st.session_state.dates.keys():
        # Use columns for better layout
        cols = st.columns([1, 2])  # Adjust column width ratios
        with cols[0]:
            # Allow user to change the date
            st.session_state.dates[date_key] = st.date_input("日付", value=st.session_state.dates[date_key], key=f"date_{date_key}")
        with cols[1]:
            # Allow user to select a dish
            st.session_state.day_to_register_dish[date_key] = st.selectbox(
                "主菜",
                options=[""] + dish_list,
                index=(
                    dish_list.index(st.session_state.day_to_register_dish[date_key]) + 1
                    if st.session_state.day_to_register_dish[date_key]
                    else 0
                ),
                key=f"dish_{date_key}",
            )
    register_dishes = st.form_submit_button("メニューを登録する")

if register_dishes:
    # Prepare data for insertion/update
    data = [{"date": date, "menu": dish} for date, dish in st.session_state.day_to_register_dish.items() if dish]

    if len(data) > 0:
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        register_dish_history(df)

        st.success("メニューが登録されました！")
    else:
        st.warning("登録するメニューが選択されていません。")

# Display past menu data
st.divider()
st.write("### 過去の登録メニュー")
past_menu_data = pd.DataFrame({"日付": date_list, "主菜": recent_menu_list})
st.dataframe(past_menu_data, hide_index=True)
