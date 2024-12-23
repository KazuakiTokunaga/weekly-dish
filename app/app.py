import streamlit as st

st.set_page_config(
    page_title="おうちの主菜",
    page_icon=":shark:",
    layout="centered",
    initial_sidebar_state="collapsed",
)


weekly_dishes = st.Page("weekly_dishes.py", title="今週の主菜")
daily_dishes = st.Page("daily_dishes.py", title="今日の主菜")
register_dishes = st.Page("register_dishes.py", title="主菜を登録")

pg = st.navigation([weekly_dishes, daily_dishes, register_dishes])

pg.run()
