import base64
import json
import os
import random
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta

from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account


@dataclass
class Menu:
    name: str
    season: str
    holiday_only: bool
    not_storable: bool
    interval: int
    cooking_method: str
    main_ingredient: str
    category: str | None


def get_menu_data() -> list[Menu]:
    load_dotenv()
    encoded_secrets = os.environ["GCP_SA_CREDENTIAL"]
    decoded_secrets = base64.b64decode(encoded_secrets).decode("utf-8")
    secrets = json.loads(decoded_secrets, strict=False)

    scopes = ["https://www.googleapis.com/auth/bigquery", "https://www.googleapis.com/auth/drive"]
    credentials = service_account.Credentials.from_service_account_info(secrets, scopes=scopes)
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)

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


def get_weekly_dish() -> tuple[list[Menu], str]:
    menu_list = get_menu_data()

    constraints_ingredients = {
        "海鮮": 2,
        "牛肉": 2,
        "豚肉": 2,
        "鶏肉": 2,
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

    if month not in [6, 7, 8, 9]:
        menu_list = [menu for menu in menu_list if menu.season != "夏"]
    elif month not in [11, 12, 1, 2, 3]:
        menu_list = [menu for menu in menu_list if menu.season != "冬"]

    for idx, day in enumerate(days_of_week):
        is_weekend = day.endswith("(Sat)") or day.endswith("(Sun)")
        is_today_or_next = idx in [0, 1]  # Today and the next day

        filtered_menu = [menu for menu in menu_list if (not menu.holiday_only or is_weekend)]
        filtered_menu = [
            menu
            for menu in filtered_menu
            if (
                (used_ingredients_counts[menu.main_ingredient] < constraints_ingredients.get(menu.main_ingredient, float("inf")))
                and (menu.category is None or used_category_counts[menu.category] < constraints_category.get(menu.category, float("inf")))
                and menu not in weekly_menu
            )
        ]
        if idx > 1:
            filtered_menu = [menu for menu in filtered_menu if not menu.not_storable]

        if not filtered_menu:
            raise ValueError("No menu available for selection based on constraints.")
        weights = [
            min(
                (5 if menu.holiday_only and is_weekend else 1) * (5 if menu.not_storable and is_today_or_next else 1),
                5,
            )
            for menu in filtered_menu
        ]
        selected_menu = random.choices(filtered_menu, weights=weights, k=1)[0]
        weekly_menu.append(selected_menu)

        used_ingredients_counts[selected_menu.main_ingredient] += 1
        if selected_menu.category:
            used_category_counts[selected_menu.category] += 1

    display_string = "\n".join(f"{day} {menu.name}" for day, menu in zip(days_of_week, weekly_menu, strict=False))

    return weekly_menu, display_string


if __name__ == "__main__":
    weekly_menu, display_string = get_weekly_dish()
    print(display_string)
