import base64
import json
import os
from dataclasses import dataclass

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


def format_number(num):
    return int(num) if num.is_integer() else num


def get_bigquery_client() -> bigquery.Client:
    load_dotenv()
    encoded_secrets = os.environ["GCP_SA_CREDENTIAL"]
    decoded_secrets = base64.b64decode(encoded_secrets).decode("utf-8")
    secrets = json.loads(decoded_secrets, strict=False)

    scopes = ["https://www.googleapis.com/auth/bigquery", "https://www.googleapis.com/auth/drive"]
    credentials = service_account.Credentials.from_service_account_info(secrets, scopes=scopes)
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)

    return client


def get_recent_menu() -> list[str]:
    client = get_bigquery_client()
    QUERY = """
        SELECT menu
        FROM my_recipe_app.dish_history
        WHERE date >= current_date('Asia/Tokyo') - 6
    """
    query_job = client.query(QUERY)

    menu_list = [row["menu"] for row in query_job]
    return menu_list
