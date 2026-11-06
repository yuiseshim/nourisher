import argparse
import os
import sys
from io import BytesIO

import streamlit as st
from PIL import Image
from dotenv import load_dotenv
from google import genai
from openai import OpenAI

from urls.meal_analyzer import analyze_meal


st.set_page_config(
  page_title="食事ログAI",
  page_icon="🍽️",
  layout="wide",
)

parser = argparse.ArgumentParser()
parser.add_argument(
  "--provider",
  choices=["gemini", "openai"],
  default="gemini",
  help="使用するAI APIプロバイダー",
)
args, _ = parser.parse_known_args(sys.argv[1:])
provider = args.provider

load_dotenv()

if provider == "gemini":
  api_key = os.getenv("GEMINI_API_KEY")
  if not api_key:
    st.error("GEMINI_API_KEY が設定されていません. .env を確認してください. ")
    st.stop()
  client = genai.Client(api_key=api_key)
else:
  api_key = os.getenv("OPENAI_API_KEY")
  if not api_key:
    st.error("OPENAI_API_KEY が設定されていません. .env を確認してください. ")
    st.stop()
  client = OpenAI(api_key=api_key)


st.title("🍽️ 食事ログAI")
provider_name = "Gemini" if provider == "gemini" else "OpenAI"
st.caption(f"食事写真をアップロードすると, {provider_name}が料理・カロリー・PFCを推定します. ")

uploaded_file = st.file_uploader(
  "食事写真をアップロードしてください",
  type=["jpg", "jpeg", "png", "webp"],
)

if uploaded_file:
  image = Image.open(BytesIO(uploaded_file.read()))

  col1, col2 = st.columns([1, 1])

  with col1:
    st.subheader("アップロード画像")
    st.image(image, use_container_width=True)

  with col2:
    st.subheader("解析")

    if st.button(f"{provider_name}で解析する", type="primary"):
      with st.spinner("解析中..."):
        result = analyze_meal(image, provider, client)
        st.session_state["analysis_result"] = result

    if "analysis_result" in st.session_state:
      result = st.session_state["analysis_result"]

      st.subheader(f"{provider_name}推定結果")
      st.json(result)

      if "total" in result:
        total = result["total"]

        st.subheader("ユーザー補正")

        meal_name = st.text_input(
          "料理名",
          value=result.get("meal_name", ""),
        )

        calories = st.number_input(
          "カロリー kcal",
          value=float(total.get("calories_kcal", 0)),
          step=10.0,
        )

        protein = st.number_input(
          "たんぱく質 g",
          value=float(total.get("protein_g", 0)),
          step=1.0,
        )

        fat = st.number_input(
          "脂質 g",
          value=float(total.get("fat_g", 0)),
          step=1.0,
        )

        carbs = st.number_input(
          "炭水化物 g",
          value=float(total.get("carbs_g", 0)),
          step=1.0,
        )

        memo = st.text_area(
          "メモ",
          value=result.get("notes", ""),
        )

        corrected = {
          "meal_name": meal_name,
          "calories_kcal": calories,
          "protein_g": protein,
          "fat_g": fat,
          "carbs_g": carbs,
          "memo": memo,
        }

        st.subheader("保存予定データ")
        st.json(corrected)

        if st.button("この内容で保存する"):
          st.success("保存しました. ※このサンプルではDB保存は未実装です. ")