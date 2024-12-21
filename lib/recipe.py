import random
from collections import defaultdict
from datetime import datetime, timedelta

from lib.util import Menu, get_bigquery_client


def get_menu_data() -> list[Menu]:
    client = get_bigquery_client()
    QUERY = "SELECT * FROM ktokunaga.my_recipe_app.main_dish"
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


def get_weekly_dish() -> tuple[list[Menu], str]:
    """
    1週間分のメニューを選定する。
    季節、休日、食材・カテゴリ使用数の制約を適用したうえで、週替わりメニューを決定する。
    """
    menu_list = get_menu_data()

    constraints_ingredients = {
        "海鮮": 2,
        "牛肉": 2,
        "豚肉": 3,
        "鶏肉": 3,
    }
    constraints_category = {
        "カレー・シチュー": 1,
        "クックドゥ": 1,
    }

    used_ingredients_counts = defaultdict(int)
    used_category_counts = defaultdict(int)

    weekly_menu = []
    today = datetime.today()
    month = today.month
    days_of_week = [(today + timedelta(days=i)).strftime("%m/%d(%a)") for i in range(7)]

    # 季節フィルタリング(週単位で一度実行)
    menu_list = filter_menu_by_season(menu_list, month)

    for idx, day_str in enumerate(days_of_week):
        is_weekend = day_str.endswith("(Sat)") or day_str.endswith("(Sun)")
        is_today_or_next = idx in [0, 1]  # 今日と翌日の判定

        # 休日によるフィルタリング(曜日ごとに異なる)
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

        # 重み付け
        weights = [min((5 if menu.holiday_only and is_weekend else 1) * (5 if menu.not_storable and is_today_or_next else 1), 5) for menu in filtered_menu]

        selected_menu = random.choices(filtered_menu, weights=weights, k=1)[0]
        weekly_menu.append(selected_menu)

        used_ingredients_counts[selected_menu.main_ingredient] += 1
        if selected_menu.category:
            used_category_counts[selected_menu.category] += 1

    display_string = "\n".join(f"{day_str} {menu.name}" for day_str, menu in zip(days_of_week, weekly_menu, strict=False))
    return weekly_menu, display_string


def get_todays_dish() -> tuple[list[Menu], str]:
    """
    今日のメニュー候補を3つ提示し、テキスト文字列も返す。
    季節・休日に応じたフィルタリングを行い、条件に合う3つのメニューをランダムサンプルで選択。
    """
    menu_list = get_menu_data()
    today = datetime.today()
    month = today.month
    weekday = today.weekday()
    is_weekend = weekday >= 5

    # 季節・休日フィルタリングを共通関数で適用
    menu_list = filter_menu_by_season(menu_list, month)
    menu_list = filter_menu_by_holiday(menu_list, is_weekend)

    if len(menu_list) < 3:
        raise ValueError("条件に合うメニューが3つ未満です。")

    todays_dishes = random.sample(menu_list, 3)
    display_string = "\n".join(f"{k+1}. {menu.name}" for k, menu in enumerate(todays_dishes))

    return todays_dishes, display_string


if __name__ == "__main__":
    weekly_menu, weekly_display = get_weekly_dish()
    print(weekly_display)

    todays_menu, todays_display = get_todays_dish()
    print("\nToday's Dishes:")
    print(todays_display)
