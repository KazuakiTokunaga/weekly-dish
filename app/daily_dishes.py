import os
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st  # type: ignore
from google.cloud import storage  # type: ignore
from lib.cache import fetch_ingredients_data, fetch_menu_data, fetch_recent_menu_list
from lib.recipe import get_todays_dish
from lib.util import Menu, format_number
from PIL import ExifTags, Image

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

    selected_dish = dishes[dish_list.index(selected_dish)]
    if selected_dish.image_filename:
        # Google Cloud Storageから画像ファイルをダウンロードして表示
        bucket_name = "ktoku-dish-images"
        blob_name = selected_dish.image_filename

        # 一時ファイルを作成してGCSから画像をダウンロード
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{blob_name.split('.')[-1]}") as temp_file:
            blob.download_to_filename(temp_file.name)

            # PILで画像を開いてExif情報に基づいて向きを修正
            try:
                image = Image.open(temp_file.name)

                # Exif情報を取得して向きを修正
                if hasattr(image, "_getexif") and image._getexif() is not None:
                    exif = dict((ExifTags.TAGS[k], v) for k, v in image._getexif().items() if k in ExifTags.TAGS)
                    if "Orientation" in exif:
                        orientation = exif["Orientation"]

                        # 向きに応じて回転処理
                        if orientation == 2:
                            image = image.transpose(Image.FLIP_LEFT_RIGHT)
                        elif orientation == 3:
                            image = image.transpose(Image.ROTATE_180)
                        elif orientation == 4:
                            image = image.transpose(Image.FLIP_TOP_BOTTOM)
                        elif orientation == 5:
                            image = image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90)
                        elif orientation == 6:
                            image = image.transpose(Image.ROTATE_270)
                        elif orientation == 7:
                            image = image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
                        elif orientation == 8:
                            image = image.transpose(Image.ROTATE_90)

                # 修正した画像を一時ファイルに保存して表示
                corrected_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                image.save(corrected_temp_file.name)
                st.image(corrected_temp_file.name)

                # 一時ファイルを削除
                os.unlink(corrected_temp_file.name)

            except Exception as e:
                st.error(f"画像処理エラー: {e}")
                # エラーが発生した場合は元の画像をそのまま表示
                st.image(temp_file.name)

            # 元の一時ファイルを削除
            os.unlink(temp_file.name)
