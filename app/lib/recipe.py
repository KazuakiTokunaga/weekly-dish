import random
from collections import defaultdict
from datetime import datetime, timedelta

import pandas as pd
from google.cloud import bigquery

from lib.util import Menu, get_bigquery_client


def get_recent_menu() -> tuple[list[str], list[str]]:
    client = get_bigquery_client()
    QUERY = """
        SELECT date, menu
        FROM my_recipe_app.dish_history
        WHERE date >= current_date('Asia/Tokyo') - 14
        ORDER BY date desc
    """
    query_job = client.query(QUERY)

    menu_list = [row["menu"] for row in query_job]
    date_list = [row["date"] for row in query_job]
    return menu_list, date_list


def get_menu_data() -> list[Menu]:
    client = get_bigquery_client()
    QUERY = "SELECT * FROM my_recipe_app.main_dish"
    query_job = client.query(QUERY)

    menu_list = [
        Menu(
            name=row["menu"],
            season=row["season"],
            holiday_only=row["holiday_flag"],
            not_storable=row["store_flag"],
            interval=row["interval"],
            cooking_method=row["utensil"],
            main_ingredient=row["main_ingredients"],
            category=row["category"],
        )
        for row in query_job
    ]

    return menu_list


def get_ingredients_data() -> pd.DataFrame:
    client = get_bigquery_client()
    QUERY = "SELECT * FROM my_recipe_app.ingredients"
    query_job = client.query(QUERY)
    df_ingredients = query_job.to_dataframe()

    return df_ingredients


def filter_menu_by_season(menu_list: list[Menu], month: int) -> list[Menu]:
    """月(季節)に応じて夏・冬メニューを除外する."""
    filtered = menu_list[:]
    if month not in [6, 7, 8, 9]:
        filtered = [menu for menu in filtered if menu.season != "夏"]
    if month not in [11, 12, 1, 2, 3]:
        filtered = [menu for menu in filtered if menu.season != "冬"]
    return filtered


def filter_menu_by_holiday(menu_list: list[Menu], is_weekend: bool) -> list[Menu]:
    return [menu for menu in menu_list if (not menu.holiday_only or is_weekend)]


def get_weekly_dish(dishes: list[Menu], recent_menu: list[str]) -> list[Menu]:
    """
    1週間分のメニューを選定する。
    季節、休日、食材・カテゴリ使用数の制約を適用したうえで、週替わりメニューを決定する。
    """

    constraints_ingredients = {
        "海鮮": 2,
        "牛肉": 2,
        "豚肉": 3,
        "鶏肉": 3,
    }
    constraints_category = {"カレー・シチュー": 1, "クックドゥ": 1, "鍋": 1}

    used_ingredients_counts: defaultdict[str, int] = defaultdict(int)
    used_category_counts: defaultdict[str, int] = defaultdict(int)

    weekly_menu = []
    today = datetime.today()
    month = today.month
    days_of_week = [(today + timedelta(days=i)).strftime("%m/%d(%a)") for i in range(7)]

    # 季節フィルタリング(週単位で一度実行)
    menu_list = filter_menu_by_season(dishes, month)
    menu_list = [menu for menu in menu_list if menu.name not in recent_menu]

    for idx, day_str in enumerate(days_of_week):
        is_weekend = day_str.endswith("(Sat)") or day_str.endswith("(Sun)")
        is_today_or_next = idx in [0, 1]

        filtered_menu = filter_menu_by_holiday(menu_list, is_weekend)

        # 使用回数制約の適用
        filtered_menu = [
            menu
            for menu in filtered_menu
            if (used_ingredients_counts[menu.main_ingredient] < constraints_ingredients.get(menu.main_ingredient, float("inf")))
            and (menu.category is None or used_category_counts[menu.category] < constraints_category.get(menu.category, float("inf")))
            and menu not in weekly_menu
        ]

        # 今日・明日以降は保存不可(not_storable)メニューを除外
        if idx > 1:
            filtered_menu = [menu for menu in filtered_menu if not menu.not_storable]

        if not filtered_menu:
            raise ValueError("No menu available for selection based on constraints.")

        weights = [5 if menu.holiday_only and is_weekend else 1 for menu in filtered_menu]
        weights = [5 if menu.not_storable and is_today_or_next else weight for menu, weight in zip(filtered_menu, weights, strict=True)]
        selected_menu = random.choices(filtered_menu, weights=weights, k=1)[0]
        weekly_menu.append(selected_menu)

        used_ingredients_counts[selected_menu.main_ingredient] += 1
        if selected_menu.category:
            used_category_counts[selected_menu.category] += 1

    return weekly_menu


def get_todays_dish(dishes: list[Menu], recent_menu: list[str]) -> Menu:
    today = datetime.today()
    month = today.month
    weekday = today.weekday()
    is_weekend = weekday >= 5

    # 季節・休日フィルタリングを共通関数で適用
    menu_list = filter_menu_by_season(dishes, month)
    menu_list = filter_menu_by_holiday(menu_list, is_weekend)
    menu_list = [menu for menu in menu_list if menu.name not in recent_menu]

    todays_dishes = random.sample(menu_list, 1)[0]

    return todays_dishes


def register_dish_history(df: pd.DataFrame) -> None:
    client = get_bigquery_client()
    table_id = "my_recipe_app.dish_history"
    schema = [
        bigquery.SchemaField("date", "DATE"),
        bigquery.SchemaField("menu", "STRING"),
    ]
    job_config = bigquery.LoadJobConfig(schema=schema, write_disposition="WRITE_TRUNCATE")
    temp_table_id = f"{table_id}_temp"
    client.load_table_from_dataframe(df, temp_table_id, job_config=job_config).result()

    # Use MERGE statement to update the main table with the temporary table
    merge_query = f"""
    MERGE `{table_id}` T
    USING `{temp_table_id}` S
    ON T.date = S.date
    WHEN MATCHED THEN
        UPDATE SET T.menu = S.menu
    WHEN NOT MATCHED THEN
        INSERT (date, menu) VALUES (S.date, S.menu)
    """
    client.query(merge_query).result()
