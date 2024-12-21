from lib.util import Ingredient, Menu, get_bigquery_client


def get_ingredients_for_menus(menus: list[Menu]) -> list[str]:
    client = get_bigquery_client()
    QUERY = "SELECT * FROM ktokunaga.my_recipe_app.ingredients"
    query_job = client.query(QUERY)
    df = query_job.to_dataframe()

    menu_names = [menu.name for menu in menus]
    df = df[df["menu"].isin(menu_names)]
    df_sum = df.groupby(["ingredients", "units"])["number"].sum().reset_index()

    ingredients = []
    for _, row in df_sum.iterrows():
        ingredient = Ingredient(
            name=row.ingredients,
            number=row.number,
            unit=row.units,
        )
        ingredients.append(ingredient)

    display_string = "\n".join(f"{ingredient.name} {ingredient.number}{ingredient.unit}" for ingredient in ingredients)

    return ingredients, display_string
