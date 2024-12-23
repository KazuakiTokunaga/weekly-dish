from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from lib.recipe import get_ingredients_data, get_menu_data, get_recent_menu, get_weekly_dish
from lib.util import Menu, format_number

# Title and header
st.title("今週の主菜")


@st.cache_data
def fetch_menu_data():
    """Fetch menu data once per session."""
    return get_menu_data()


@st.cache_data
def fetch_ingredients_data():
    """Fetch ingredients data once per session."""
    return get_ingredients_data()


@st.cache_data
def get_recent_menu_list():
    """Fetch recent menu data once per session."""
    return get_recent_menu()


def generate_week_dates():
    """Generate week dates once per session."""
    today = datetime.now(ZoneInfo("Asia/Tokyo"))
    return [(today + timedelta(days=i)).strftime("%m/%d(%a)") for i in range(7)]


# Load data
dishes: list[Menu] = fetch_menu_data()
dish_list = [dish.name for dish in dishes]

df_ingredients: pd.DataFrame = fetch_ingredients_data()
recent_menu: list[str] = get_recent_menu_list()

dates = generate_week_dates()

# Session state to retain selections if "材料を表示する" button is pressed
if "day_to_dish" not in st.session_state:
    st.session_state.day_to_dish = {date: "" for date in dates}

# Suggest dishes button
if st.button("主菜リストを提案する"):
    weekly_dishes = get_weekly_dish(dishes, recent_menu)
    weekly_dishes_name = [dish.name for dish in weekly_dishes]
    st.session_state.day_to_dish = {date: dish for date, dish in zip(dates, weekly_dishes_name, strict=False)}

# User input for each day
st.write("### 1週間分の主菜を選択")
with st.form(key="dish_selection_form"):
    for date in dates:
        st.session_state.day_to_dish[date] = st.selectbox(
            f"{date} の主菜を選択",
            options=[""] + dish_list,
            index=(dish_list.index(st.session_state.day_to_dish[date]) + 1 if st.session_state.day_to_dish[date] else 0),
            key=date,
        )
    show_ingredients = st.form_submit_button("材料を表示する")

if show_ingredients:
    st.write("### 材料リスト")

    display_ingredients: str = ""
    df_target_accum = pd.DataFrame()
    for day, dish in st.session_state.day_to_dish.items():
        display_ingredients += f"{day}: {dish}"
        df_target = df_ingredients[df_ingredients["menu"] == dish]
        df_target_accum = pd.concat([df_target_accum, df_target], ignore_index=True)
        ingredients = [f"{row['ingredients']} {format_number(row['number'])}{row['units']}" for _, row in df_target.iterrows()]
        display_ingredients += "\n" + "\n".join(ingredients)
        display_ingredients += "\n\n"
    st.text(display_ingredients)

    st.write("### 材料リスト(合計)")
    df_target_accum = df_target_accum.groupby("ingredients").agg({"number": "sum", "units": "first"}).reset_index()
    ingredients = [f"{row['ingredients']} {format_number(row['number'])}{row['units']}" for _, row in df_target_accum.iterrows()]
    st.text("\n".join(ingredients))
else:
    st.write("\n")
