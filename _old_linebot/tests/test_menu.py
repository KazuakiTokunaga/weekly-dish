from lib.ingredients import get_ingredients_for_menus
from lib.util import Ingredient, Menu


def test_get_ingredients_for_single_menu():
    menus = [
        Menu(
            name="ビーフシチュー",
            season="通年",
            holiday_only=False,
            not_storable=False,
            interval=1,
            cooking_method="ホットクック",
            main_ingredient="牛肉",
            category="カレー・シチュー",
        )
    ]
    ingredients, display_string = get_ingredients_for_menus(menus)
    display_name = [line.split(" ")[0] for line in display_string.split("\n")]

    expected_ingredients = [
        Ingredient(
            name="牛すね肉",
            number=250,
            unit="グラム",
        ),
        Ingredient(
            name="玉ねぎ",
            number=1,
            unit="個",
        ),
        Ingredient(
            name="人参",
            number=0.5,
            unit="本",
        ),
        Ingredient(
            name="じゃがいも",
            number=1,
            unit="個",
        ),
        Ingredient(
            name="ビーフシチューのもと",
            number=0.5,
            unit="箱",
        ),
    ]
    expected_display_name = ["牛すね肉", "玉ねぎ", "人参", "じゃがいも", "ビーフシチューのもと"]

    def sort_key(ingredient):
        return (ingredient.name, ingredient.number, ingredient.unit)

    assert sorted(ingredients, key=sort_key) == sorted(expected_ingredients, key=sort_key)
    assert set(display_name) == set(expected_display_name)


def test_get_ingredients_for_multiple_menu():
    menus = [
        Menu(
            name="ビーフシチュー",
            season="通年",
            holiday_only=False,
            not_storable=False,
            interval=1,
            cooking_method="ホットクック",
            main_ingredient="牛肉",
            category="カレー・シチュー",
        ),
        Menu(
            name="クリームシチュー",
            season="通年",
            holiday_only=False,
            not_storable=False,
            interval=1,
            cooking_method="ホットクック",
            main_ingredient="鶏肉",
            category="カレー・シチュー",
        ),
    ]
    ingredients, display_string = get_ingredients_for_menus(menus)
    display_name = [line.split(" ")[0] for line in display_string.split("\n")]

    expected_ingredients = [
        Ingredient(
            name="牛すね肉",
            number=250,
            unit="グラム",
        ),
        Ingredient(
            name="玉ねぎ",
            number=2,
            unit="個",
        ),
        Ingredient(
            name="人参",
            number=1,
            unit="本",
        ),
        Ingredient(
            name="じゃがいも",
            number=2,
            unit="個",
        ),
        Ingredient(
            name="ビーフシチューのもと",
            number=0.5,
            unit="箱",
        ),
        Ingredient(
            name="鶏もも肉",
            number=250,
            unit="グラム",
        ),
        Ingredient(
            name="クリームシチューのもと",
            number=0.5,
            unit="箱",
        ),
    ]
    expected_display_name = ["牛すね肉", "玉ねぎ", "人参", "じゃがいも", "ビーフシチューのもと", "鶏もも肉", "クリームシチューのもと"]

    def sort_key(ingredient):
        return (ingredient.name, ingredient.number, ingredient.unit)

    assert sorted(ingredients, key=sort_key) == sorted(expected_ingredients, key=sort_key)
    assert set(display_name) == set(expected_display_name)
