from collections import defaultdict

import pandas as pd
from lib.recipe import filter_menu_by_holiday, filter_menu_by_season, get_ingredients_data, get_menu_data, get_recent_menu, get_weekly_dish
from lib.util import Menu

# Load data
dishes: list[Menu] = get_menu_data()
dish_list = [dish.name for dish in dishes]

df_ingredients: pd.DataFrame = get_ingredients_data()
recent_menu: list[str] = get_recent_menu()


def test_get_weekly_dish():
    constraints_ingredients = {
        "海鮮": 2,
        "牛肉": 2,
        "豚肉": 3,
        "鶏肉": 3,
    }
    constraints_category = {"カレー・シチュー": 1, "クックドゥ": 1, "鍋": 1}

    for _ in range(10):
        weekly_menu = get_weekly_dish(dishes, recent_menu)

        # 1週間のメニューの名前とそのセットの長さを確認
        weekly_menu_names = [menu.name for menu in weekly_menu]
        assert len(weekly_menu) == 7
        assert len(set(weekly_menu_names)) == 7

        # 食材の使用回数をカウント
        used_ingredients_counts = defaultdict(int)
        used_category_counts = defaultdict(int)

        for menu in weekly_menu:
            used_ingredients_counts[menu.main_ingredient] += 1
            if menu.category:
                used_category_counts[menu.category] += 1

        # 食材使用回数の制約を確認
        for ingredient, max_count in constraints_ingredients.items():
            assert (
                used_ingredients_counts[ingredient] <= max_count
            ), f"{ingredient} used {used_ingredients_counts[ingredient]} times, exceeding {max_count}"

        # カテゴリ使用回数の制約を確認
        for category, max_count in constraints_category.items():
            assert (
                used_category_counts[category] <= max_count
            ), f"{category} used {used_category_counts[category]} times, exceeding {max_count}"


def tests_weekend_filter():
    # テスト用のメニューリスト
    menus = [
        Menu(
            name="ローストビーフ",
            season="通年",
            holiday_only=True,
            not_storable=True,
            interval=1,
            cooking_method="ホットクック",
            main_ingredient="牛肉",
            category=None,
        ),
        Menu(
            name="カレー",
            season="通年",
            holiday_only=False,
            not_storable=False,
            interval=1,
            cooking_method="ホットクック",
            main_ingredient="豚肉",
            category="カレー・シチュー",
        ),
    ]

    # 平日でフィルタリング
    is_weekend = False
    filtered_weekday = filter_menu_by_holiday(menus, is_weekend)

    # 休日でフィルタリング
    is_weekend = True
    filtered_weekend = filter_menu_by_holiday(menus, is_weekend)

    # 平日では、holiday_only=True のメニューは含まれない
    assert len(filtered_weekday) == 1
    assert filtered_weekday[0].name == "カレー"

    # 休日では、全てのメニューが含まれる
    assert len(filtered_weekend) == 2
    assert "ローストビーフ" in [menu.name for menu in filtered_weekend]
    assert "カレー" in [menu.name for menu in filtered_weekend]


def test_filter_menu_by_season():
    # テスト用のメニューリスト
    menus = [
        Menu(
            name="豚冷しゃぶ",
            season="夏",
            holiday_only=False,
            not_storable=True,
            interval=1,
            cooking_method="鍋",
            main_ingredient="鶏肉",
            category=None,
        ),
        Menu(
            name="鍋（豚肉）",
            season="冬",
            holiday_only=False,
            not_storable=False,
            interval=1,
            cooking_method="ホットクック",
            main_ingredient="豚肉",
            category="鍋",
        ),
        Menu(
            name="カレー",
            season="通年",
            holiday_only=False,
            not_storable=False,
            interval=1,
            cooking_method="ホットクック",
            main_ingredient="豚肉",
            category="カレー・シチュー",
        ),
    ]

    # 夏 (6月) の場合
    summer_month = 6
    filtered_summer = filter_menu_by_season(menus, summer_month)
    assert len(filtered_summer) == 2
    assert "豚冷しゃぶ" in [menu.name for menu in filtered_summer]
    assert "カレー" in [menu.name for menu in filtered_summer]
    assert "鍋（豚肉）" not in [menu.name for menu in filtered_summer]

    # 冬 (12月) の場合
    winter_month = 12
    filtered_winter = filter_menu_by_season(menus, winter_month)
    assert len(filtered_winter) == 2
    assert "鍋（豚肉）" in [menu.name for menu in filtered_winter]
    assert "カレー" in [menu.name for menu in filtered_winter]
    assert "豚冷しゃぶ" not in [menu.name for menu in filtered_winter]

    # 通年 (春: 4月) の場合
    spring_month = 4
    filtered_spring = filter_menu_by_season(menus, spring_month)
    assert len(filtered_spring) == 1
    assert "カレー" in [menu.name for menu in filtered_spring]
    assert "豚冷しゃぶ" not in [menu.name for menu in filtered_spring]
    assert "鍋（豚肉）" not in [menu.name for menu in filtered_spring]
