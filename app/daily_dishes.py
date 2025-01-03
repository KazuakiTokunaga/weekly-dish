from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from lib.cache import fetch_ingredients_data, fetch_menu_data, fetch_recent_menu_list
from lib.recipe import get_todays_dish
from lib.util import Menu, format_number

# Title and header
st.title("今日の主菜")


# Load data
dishes: list[Menu] = fetch_menu_data()
dish_list = [dish.name for dish in dishes]

df_ingredients: pd.DataFrame = fetch_ingredients_data()
recent_menu: list[str] = fetch_recent_menu_list()[0][:7]

# Get today's date in Japan time
today = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%m/%d(%a)")

# Session state to retain selections if "材料を表示" button is pressed
if "selected_dish" not in st.session_state:
    st.session_state.selected_dish = ""

# Suggest dish button
if st.button("主菜を提案"):
    st.session_state.selected_dish = get_todays_dish(dishes, recent_menu).name

# User input for today's dish
st.session_state.selected_dish = st.selectbox(
    f"{today}: 主菜を選択",
    options=[""] + dish_list,
    index=(dish_list.index(st.session_state.selected_dish) + 1 if st.session_state.selected_dish else 0),
)

# Display ingredients if a dish is selected
selected_dish = st.session_state.selected_dish
if selected_dish:
    df_target = df_ingredients[df_ingredients["menu"] == selected_dish]
    ingredients = [f"{row['ingredients']} {format_number(row['number'])}{row['units']}" for _, row in df_target.iterrows()]
    st.text("\n".join(ingredients))
